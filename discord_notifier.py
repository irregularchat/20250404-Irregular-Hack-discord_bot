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
            # Extract email data
            subject = email_data.get('subject', 'No Subject')
            sender = email_data.get('from', 'Unknown')
            date = email_data.get('date', 'Unknown')
            summary = email_data.get('summary', '')
            body = email_data.get('body', '')
            body_length = len(body)
            
            # Create an embed for the email
            embed = discord.Embed(
                title=f"📧 {subject}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add email details to embed
            embed.add_field(name="From", value=sender, inline=True)
            embed.add_field(name="Date", value=date, inline=True)
            embed.add_field(name="Email Length", value=f"{body_length} characters", inline=True)
            
            # Add summary if available - this is the AI-generated content analysis
            if summary:
                embed.add_field(name="📝 Content Analysis", value=summary, inline=False)
            
            # Add a snippet of the body
            if body:
                # Truncate body if it's too long for Discord
                max_preview_length = 800  # Shorter preview to keep embed compact
                truncated_body = body[:max_preview_length] + "..." if body_length > max_preview_length else body
                embed.add_field(name="📄 Content Preview", value=f"```{truncated_body}```", inline=False)
                
                # Set footer to indicate content length
                if body_length > max_preview_length:
                    embed.set_footer(text=f"Full email: {body_length} characters ({round(body_length/max_preview_length, 1)}x longer than preview)")
            
            # Send the embed to the channel
            await channel.send(embed=embed)
            logger.info(f"Sent notification for email: {subject} - {body_length} characters")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
