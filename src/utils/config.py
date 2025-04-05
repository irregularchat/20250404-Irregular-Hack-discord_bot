import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email settings
IMAP_SERVER = os.getenv("imap_server")
IMAP_USER = os.getenv("imap_user")
IMAP_PASSWORD = os.getenv("imap_password")
IMAP_PORT = int(os.getenv("imap_port", 993))
IMAP_SSL = os.getenv("imap_ssl", "true").lower() == "true"
WHITELISTED_EMAIL_ADDRESSES = os.getenv("whitelisted_email_addresses", "").split(",")

# OpenAI settings
OPENAI_API_KEY = os.getenv("openai_api_key")

# Discord settings
DISCORD_TOKEN = os.getenv("discord_token")
DISCORD_CHANNEL_ID = int(os.getenv("discord_channel_id")) if os.getenv("discord_channel_id") else None

# System settings
CHECK_INTERVAL = int(os.getenv("check_interval", 60))  # Default to 60 seconds

# Logging settings
LOG_LEVEL = os.getenv("log_level", "INFO")
LOG_CONCISE = os.getenv("log_concise", "false").lower() == "true"
LOG_TO_FILE = os.getenv("log_to_file", "false").lower() == "true"
LOG_FILE = os.getenv("log_file", "email_monitor.log")
