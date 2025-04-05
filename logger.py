import logging
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors for different log levels
LOG_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels in console output
    """

    def format(self, record):
        # Get the original formatted message
        msg = super().format(record)
        # Add color based on log level
        if record.levelno in LOG_COLORS:
            # Format: apply color to the level name only
            level_name = record.levelname
            colored_level = f"{LOG_COLORS[record.levelno]}{level_name}{Style.RESET_ALL}"
            # Replace the level name with the colored version
            msg = msg.replace(level_name, colored_level)
        return msg


def get_logger(
    name: str = None,
    level: int = logging.INFO,
    console: bool = True,
    file: bool = False,
    log_file: str = None,
    concise: bool = False,
) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and level.

    Args:
        name (str): Logger name
        level (int): Logging level (default: logging.INFO)
        console (bool): Whether to log to console (default: True)
        file (bool): Whether to log to file (default: False)
        log_file (str): Path to log file (default: None, uses config.LOG_FILE if available)
        concise (bool): Use concise output format (default: False)

    Returns:
        logging.Logger: Configured logger
    """
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()

    # Create formatters
    if concise:
        # Concise format without timestamp and logger name for cleaner output
        console_format = "%(levelname)-8s %(message)s"
        file_format = "%(asctime)s [%(levelname)-8s] %(message)s"
    else:
        # Standard format with all details
        console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Use colored formatter for console
        colored_formatter = ColoredFormatter(console_format)
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

    # Add file handler if requested
    if file:
        # Try to get log file from config if not provided
        if not log_file:
            try:
                import config

                log_file = getattr(config, "LOG_FILE", None)
            except (ImportError, AttributeError):
                log_file = "app.log"

        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
