import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email configuration
IMAP_SERVER = os.getenv('imap_server')
IMAP_USER = os.getenv('imap_user')
IMAP_PASSWORD = os.getenv('imap_password')
IMAP_PORT = int(os.getenv('imap_port', 993))

# OpenAI configuration
OPENAI_API_KEY = os.getenv('openai_api_key')

# Discord configuration
DISCORD_TOKEN = os.getenv('discord_token')
DISCORD_CHANNEL_ID = int(os.getenv('discord_channel_id')) if os.getenv('discord_channel_id') else None

# Email filtering
# Parse whitelist and strip whitespace from each address
WHITELISTED_EMAIL_ADDRESSES = [email.strip() for email in os.getenv('whitelisted_email_addresses', '').split(',')] if os.getenv('whitelisted_email_addresses') else []

# Bot configuration
CHECK_INTERVAL = 300  # Check for new emails every 5 minutes by default
