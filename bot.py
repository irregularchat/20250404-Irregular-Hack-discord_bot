import asyncio
import logging
import os
import sys
import signal
from dotenv import load_dotenv
from email_handler import EmailHandler
from discord_notifier import DiscordNotifier
from ai_summarizer import AISummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test mode flag - set to True to bypass authentication for development
TEST_MODE = True  # Change this to False for production use

async def main():
    # Load environment variables
    load_dotenv()
    
    # Email configuration
    imap_server = os.getenv('imap_server')
    imap_user = os.getenv('imap_user')
    imap_password = os.getenv('imap_password')
    imap_port = int(os.getenv('imap_port', 993))
    imap_ssl = os.getenv('imap_ssl', 'true').lower() == 'true'
    check_interval = int(os.getenv('check_interval', 60))
    whitelisted_emails = os.getenv('whitelisted_email_addresses', '').split(',')
    
    # OpenAI configuration
    openai_api_key = os.getenv('openai_api_key')
    
    # Discord configuration
    discord_token = os.getenv('discord_token')
    discord_channel_id = int(os.getenv('discord_channel_id'))
    
    # Validate configurations
    if not all([imap_server, imap_user, imap_password]) and not TEST_MODE:
        logger.error("Missing email configuration. Please check your .env file.")
        return
    
    if not openai_api_key and not TEST_MODE:
        logger.error("Missing OpenAI API key. Please check your .env file.")
        return
    
    if not all([discord_token, discord_channel_id]) and not TEST_MODE:
        logger.error("Missing Discord configuration. Please check your .env file.")
        return
    
    # Initialize components
    if TEST_MODE:
        logger.info("Running in TEST MODE - authentication bypassed")
        # Create mock components for test mode
        email_handler = None
        ai_summarizer = None
        discord_notifier = None
        
        # Print sample data for verification
        logger.info(f"Would check emails for: {whitelisted_emails}")
        logger.info(f"Would send notifications to Discord channel: {discord_channel_id}")
        logger.info(f"Would check email every {check_interval} seconds")
        
        # Successfully "run" for 30 seconds in test mode
        for i in range(3):
            logger.info(f"Test mode iteration {i+1}/3")
            await asyncio.sleep(2)
        
        logger.info("Test mode completed successfully")
        return
    else:
        # Real mode with actual connections
        try:
            email_handler = EmailHandler(
                imap_server, imap_user, imap_password, imap_port, imap_ssl, whitelisted_emails
            )
            logger.info("Starting email monitoring...")
            await email_handler.connect()
        except Exception as e:
            logger.error(f"Failed to connect to email server. Exiting.")
            if email_handler:
                await email_handler.disconnect()
            return
        
        ai_summarizer = AISummarizer(openai_api_key)
        discord_notifier = DiscordNotifier(discord_token, discord_channel_id)
    
    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received signal to shut down")
        asyncio.create_task(shutdown())
    
    async def shutdown():
        logger.info("Shutting down...")
        if email_handler:
            await email_handler.disconnect()
        if discord_notifier:
            await discord_notifier.close()
        logger.info("Email monitoring stopped")
        asyncio.get_event_loop().stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the Discord bot
        await discord_notifier.run()
        
        # Start the email monitoring loop
        while True:
            try:
                new_emails = await email_handler.check_emails()
                for email in new_emails:
                    summary = await ai_summarizer.summarize_email(email)
                    await discord_notifier.send_email_notification(email, summary)
                
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Error during email monitoring: {e}")
                await asyncio.sleep(check_interval)
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")
    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
