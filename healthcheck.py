#!/usr/bin/env python3
"""
Simple health check script for the Discord bot
"""
import os
import sys
import psutil
from logger import get_logger

logger = get_logger(__name__)


def is_bot_running():
    """Check if the bot process is running"""
    try:
        # Check for "bot.py" process
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if proc.info["cmdline"] and "bot.py" in " ".join(proc.info["cmdline"]):
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking process: {e}")
        return False


def main():
    """Main health check function"""
    # Check if the bot.py file exists
    if not os.path.exists("bot.py"):
        logger.error("bot.py file not found")
        sys.exit(1)

    # Check if the bot process is running
    if not is_bot_running():
        logger.error("Bot process not running")
        sys.exit(1)

    logger.info("Health check passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
