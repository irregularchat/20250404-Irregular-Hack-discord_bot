import asyncio
import logging
import sys
from src.utils import config
from src.utils.logger import get_logger
from src.email_monitor_bot import EmailMonitorBot

# Get logger with configuration from config
logger = get_logger(
    __name__,
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    concise=config.LOG_CONCISE,
    file=config.LOG_TO_FILE,
    log_file=config.LOG_FILE,
)

# Enable debug logging if specified
DEBUG_LOGGING = False  # Enable debug logging for testing email body processing
if DEBUG_LOGGING:
    logger.setLevel(logging.DEBUG)
    logger.debug("Debug logging enabled")

# Test mode flag - set to True for development/testing
TEST_MODE = False  # Change this to True for development/testing


# Simple main function - non-async
async def main():
    """Main entry point for the application"""
    # Check for missing email configuration
    if not all([config.IMAP_SERVER, config.IMAP_USER, config.IMAP_PASSWORD]):
        logger.error("Missing email configuration. Please check your .env file.")
        return

    # Check for missing OpenAI configuration
    if not config.OPENAI_API_KEY:
        logger.error("Missing OpenAI API key. Please check your .env file.")
        return

    # Check for missing Discord configuration
    if not all([config.DISCORD_TOKEN, config.DISCORD_CHANNEL_ID]):
        logger.error("Missing Discord configuration. Please check your .env file.")
        return

    # Create and run the bot if all configs are valid
    bot = EmailMonitorBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
