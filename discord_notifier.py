import discord
import logging
import config
from discord.ext import commands, tasks

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiscordNotifier(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Channel to send notifications to
        self.notification_channel_id = config.DISCORD_CHANNEL_ID
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Check if notification channel is set
        if not self.notification_channel_id:
            logger.error("Notification channel ID not set in config")
            return
        
        # Verify channel exists
        channel = self.get_channel(self.notification_channel_id)
        if not channel:
            logger.error(f"Could not find channel with ID {self.notification_channel_id}")
            return
        
        logger.info(f"Will send notifications to channel: {channel.name}")
    
    async def send_email_notification(self, email_data):
        """
        Send an email notification to the Discord channel
        
        Args:
            email_data (dict): Dictionary containing email details and summary
        """
        if not self.notification_channel_id:
            logger.error("Notification channel ID not set in config")
            return False
        
        channel = self.get_channel(self.notification_channel_id)
        if not channel:
            logger.error(f"Could not find channel with ID {self.notification_channel_id}")
            return False
        
        try:
            # Create an embed for the email
            embed = discord.Embed(
                title=email_data.get('subject', 'No Subject'),
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add email details to embed
            embed.add_field(name="From", value=email_data.get('from', 'Unknown'), inline=False)
            embed.add_field(name="Date", value=email_data.get('date', 'Unknown'), inline=False)
            
            # Add summary if available
            if 'summary' in email_data and email_data['summary']:
                embed.add_field(name="Summary", value=email_data['summary'], inline=False)
            
            # Add a snippet of the body
            body = email_data.get('body', '')
            if body:
                # Truncate body if it's too long for Discord
                max_body_length = 1000
                truncated_body = body[:max_body_length] + "..." if len(body) > max_body_length else body
                embed.add_field(name="Content Preview", value=truncated_body, inline=False)
            
            # Send the embed to the channel
            await channel.send(embed=embed)
            logger.info(f"Sent notification for email: {email_data.get('subject', 'No Subject')}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
