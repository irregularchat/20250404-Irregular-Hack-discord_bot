import asyncio
import logging
import time
from datetime import datetime
import discord
from discord.ext import commands, tasks

import config
from email_handler import EmailHandler
from ai_summarizer import summarize_email
from discord_notifier import DiscordNotifier

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailMonitorBot:
    def __init__(self):
        self.email_handler = EmailHandler()
        self.discord_bot = DiscordNotifier()
        self.running = False
    
    async def check_emails(self):
        """Check for new emails and process them"""
        logger.info("Checking for new emails...")
        
        # Get new emails
        emails = self.email_handler.get_new_emails()
        
        if not emails:
            logger.info("No new emails found")
            return
        
        logger.info(f"Found {len(emails)} new emails to process")
        
        # Process each email
        for email_data in emails:
            # Summarize email
            email_with_summary = summarize_email(email_data)
            
            # Send notification to Discord
            await self.discord_bot.send_email_notification(email_with_summary)
            
            # Add a small delay between processing emails
            await asyncio.sleep(1)
    
    async def start_monitoring(self):
        """Start the email monitoring loop"""
        self.running = True
        
        logger.info("Starting email monitoring...")
        
        # Connect to email server
        if not self.email_handler.connect():
            logger.error("Failed to connect to email server. Exiting.")
            return
        
        # Main monitoring loop
        while self.running:
            try:
                await self.check_emails()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            
            # Wait for the next check interval
            logger.info(f"Waiting {config.CHECK_INTERVAL} seconds until next check...")
            await asyncio.sleep(config.CHECK_INTERVAL)
    
    def stop_monitoring(self):
        """Stop the email monitoring loop"""
        self.running = False
        self.email_handler.disconnect()
        logger.info("Email monitoring stopped")
    
    async def run(self):
        """Run the bot"""
        # Start the monitoring task
        monitor_task = asyncio.create_task(self.start_monitoring())
        
        # Run the Discord bot
        try:
            await self.discord_bot.start(config.DISCORD_TOKEN)
        except Exception as e:
            logger.error(f"Error running Discord bot: {str(e)}")
        finally:
            # Clean up
            self.stop_monitoring()
            await self.discord_bot.close()

async def main():
    """Main entry point for the application"""
    # Check if required config is set
    if not config.IMAP_SERVER or not config.IMAP_USER or not config.IMAP_PASSWORD:
        logger.error("Email configuration is incomplete. Please check your .env file.")
        return
    
    if not config.OPENAI_API_KEY:
        logger.error("OpenAI API key is not set. Please check your .env file.")
        return
    
    if not config.DISCORD_TOKEN or not config.DISCORD_CHANNEL_ID:
        logger.error("Discord configuration is incomplete. Please check your .env file.")
        return
    
    # Create and run the bot
    bot = EmailMonitorBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
