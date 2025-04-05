import os
import sys
import psutil
from src.utils.logger import get_logger

# Set up logger
logger = get_logger(__name__)

def check_bot_file_exists():
    """Check if the bot.py file exists in the current directory"""
    if not os.path.exists("src/bot.py"):
        logger.error("Bot file not found: src/bot.py")
        return False
    logger.info("Bot file found: src/bot.py")
    return True

def check_bot_process_running():
    """Check if the bot process is running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if 'bot.py' is in the command line
            if proc.info['cmdline'] and any('bot.py' in cmd for cmd in proc.info['cmdline']):
                logger.info(f"Bot process is running (PID: {proc.info['pid']})")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    logger.error("Bot process is not running")
    return False

def main():
    """Run health checks and exit with appropriate code"""
    # Run checks
    file_check = check_bot_file_exists()
    process_check = check_bot_process_running()
    
    # Exit with code 1 if any check fails
    if not (file_check and process_check):
        sys.exit(1)
    
    # Exit with code 0 if all checks pass
    sys.exit(0)

if __name__ == "__main__":
    main()
