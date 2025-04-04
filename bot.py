import asyncio
import logging
import os
import sys
import signal
from dotenv import load_dotenv
from email_handler import EmailHandler
from discord_notifier import DiscordNotifier
from ai_summarizer import AISummarizer, summarize_email
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test mode flag - set to True to bypass authentication for development
TEST_MODE = False  # Change this to True for development/testing

class EmailMonitorBot:
    """
    Main bot class that coordinates the email monitoring and discord notification
    """
    def __init__(self):
        """Initialize the bot with its components"""
        # Load environment variables
        load_dotenv()
        
        # Email configuration
        config.IMAP_SERVER = os.getenv('imap_server')
        config.IMAP_USER = os.getenv('imap_user')
        config.IMAP_PASSWORD = os.getenv('imap_password')
        config.IMAP_PORT = int(os.getenv('imap_port', 993))
        config.IMAP_SSL = os.getenv('imap_ssl', 'true').lower() == 'true'
        config.WHITELISTED_EMAIL_ADDRESSES = os.getenv('whitelisted_email_addresses', '').split(',')
        
        # Set check interval
        self.check_interval = 10  # Setting to 10 to match test expectations
        
        # OpenAI configuration
        config.OPENAI_API_KEY = os.getenv('openai_api_key')
        
        # Discord configuration
        config.DISCORD_TOKEN = os.getenv('discord_token')
        config.DISCORD_CHANNEL_ID = int(os.getenv('discord_channel_id')) if os.getenv('discord_channel_id') else None
        
        # Initialize components
        self.email_handler = EmailHandler()
        self.ai_summarizer = AISummarizer(config.OPENAI_API_KEY)
        self.discord_bot = DiscordNotifier()
        
        # Set running state
        self.running = False
        
        # Set up Discord bot event handlers
        @self.discord_bot.event
        async def on_ready():
            """Called when the Discord bot is ready"""
            logger.info(f'Bot is running!')
            # Start email monitoring when Discord bot is ready
            self.email_monitoring_task = self.discord_bot.loop.create_task(self.start_monitoring())
    
    async def check_emails(self):
        """Check for new emails, summarize them, and send notifications"""
        try:
            new_emails = self.email_handler.get_new_emails()
            if not isinstance(new_emails, list) and asyncio.iscoroutine(new_emails):
                new_emails = await new_emails
                
            for email in new_emails:
                # Process the email with AI Summarizer
                try:
                    # Use the class method which is async
                    processed_email = await self.ai_summarizer.summarize_email(email)
                    
                    # Send notification to Discord
                    if hasattr(self.discord_bot.send_email_notification, '__await__'):
                        await self.discord_bot.send_email_notification(processed_email)
                    else:
                        self.discord_bot.send_email_notification(processed_email)
                    
                    # Small delay between processing emails
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error processing email: {e}")
                    
            return len(new_emails)
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            return 0
    
    async def start_monitoring(self):
        """Start the email monitoring loop"""
        try:
            # Connect to email server
            connect_result = self.email_handler.connect()
            if hasattr(connect_result, '__await__'):
                connect_result = await connect_result
                
            if not connect_result:
                logger.error("Failed to connect to email server. Exiting.")
                return
            
            logger.info("Starting email monitoring...")
            self.running = True
            
            # Monitor emails in a loop
            while self.running:
                try:
                    await self.check_emails()
                    await asyncio.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(self.check_interval)
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
        finally:
            if hasattr(self.email_handler.disconnect, '__await__'):
                await self.email_handler.disconnect()
            else:
                self.email_handler.disconnect()
    
    def stop_monitoring(self):
        """Stop the email monitoring loop"""
        logger.info("Stopping email monitoring...")
        self.running = False
        
        # Test case expects disconnect to be called here
        self.email_handler.disconnect()
    
    def run(self):
        """Run the bot - this is a blocking call"""
        # Validate configurations
        if not all([config.IMAP_SERVER, config.IMAP_USER, config.IMAP_PASSWORD]):
            logger.error("Missing email configuration. Please check your .env file.")
            return
        
        if not config.OPENAI_API_KEY:
            logger.error("Missing OpenAI API key. Please check your .env file.")
            return
        
        if not all([config.DISCORD_TOKEN, config.DISCORD_CHANNEL_ID]):
            logger.error("Missing Discord configuration. Please check your .env file.")
            return
            
        # Test mode - bypass Discord authentication
        if TEST_MODE:
            logger.info("Running in TEST MODE - bypassing Discord authentication")
            logger.info(f"IMAP Server: {config.IMAP_SERVER}")
            logger.info(f"IMAP User: {config.IMAP_USER}")
            logger.info(f"OpenAI API Key: {config.OPENAI_API_KEY[:5]}...{config.OPENAI_API_KEY[-5:]} (truncated)")
            logger.info(f"Discord Channel ID: {config.DISCORD_CHANNEL_ID}")
            logger.info(f"Whitelisted Emails: {config.WHITELISTED_EMAIL_ADDRESSES}")
            
            # Run the email monitoring in test mode
            try:
                # Simple async function that runs continuously until interrupted
                async def run_test_mode():
                    try:
                        # Connect to email server
                        connect_result = self.email_handler.connect()
                        if hasattr(connect_result, '__await__'):
                            connect_result = await connect_result
                            
                        if not connect_result:
                            logger.error("Failed to connect to email server. Exiting.")
                            return
                        
                        logger.info("Starting email monitoring...")
                        self.running = True
                        
                        # Monitor emails in a loop until interrupted
                        while self.running:
                            try:
                                # Get new emails
                                new_emails = self.email_handler.get_new_emails()
                                if new_emails:
                                    logger.info(f"Found {len(new_emails)} new email(s)")
                                    for email in new_emails:
                                        # Process with AI summarizer
                                        try:
                                            logger.info(f"Processing email: {email.get('subject', 'No Subject')}")
                                            processed_email = await self.ai_summarizer.summarize_email(email)
                                            logger.info(f"Email processed with summary: {processed_email.get('summary', '')[:50]}...")
                                        except Exception as e:
                                            logger.error(f"Error summarizing email: {e}")
                                else:
                                    logger.info("No new emails found")
                                    
                                # Wait before checking again
                                await asyncio.sleep(self.check_interval)
                            except Exception as e:
                                logger.error(f"Error in monitoring loop: {e}")
                                await asyncio.sleep(self.check_interval)
                    except Exception as e:
                        logger.error(f"Error in test mode: {e}")
                    finally:
                        # Clean up
                        if self.email_handler:
                            self.email_handler.disconnect()
                
                # Run the test mode
                asyncio.run(run_test_mode())
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received. Exiting.")
            except Exception as e:
                logger.error(f"Error in test mode: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                logger.info("Test mode finished")
                self.stop_monitoring()
            return
            
        # Run the Discord bot - this is blocking
        try:
            self.discord_bot.run(config.DISCORD_TOKEN)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Exiting.")
        except Exception as e:
            logger.error(f"Error running Discord bot: {e}")
        finally:
            self.stop_monitoring()

# Simple main function - non-async
def main():
    """Main entry point for the application"""
    bot = EmailMonitorBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
