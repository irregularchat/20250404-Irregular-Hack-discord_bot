import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
IMAP_SERVER = os.getenv('imap_server')
IMAP_USER = os.getenv('imap_user')
IMAP_PASSWORD = os.getenv('imap_password')
IMAP_PORT = int(os.getenv('imap_port', '993'))
IMAP_SSL = os.getenv('imap_ssl', 'true').lower() == 'true'

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('openai_api_key')

# Discord configuration
DISCORD_TOKEN = os.getenv('discord_token')
DISCORD_CHANNEL_ID = os.getenv('discord_channel_id')
if DISCORD_CHANNEL_ID and DISCORD_CHANNEL_ID.isdigit():
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)

# Monitoring configuration
CHECK_INTERVAL = int(os.getenv('check_interval', '60'))  # Default to 60 seconds

# Email whitelist
WHITELISTED_EMAIL_ADDRESSES = os.getenv('whitelisted_email_addresses', '')
WHITELISTED_EMAIL_ADDRESSES = [email.strip() for email in WHITELISTED_EMAIL_ADDRESSES.split(',') if email.strip()]

# Logging configuration
LOG_DIR = os.getenv('log_dir', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'discord_bot.log')
