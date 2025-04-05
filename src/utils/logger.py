import logging
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log level names in console output
    """
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
        return super().format(record)

def get_logger(name, level=logging.INFO, concise=False, file=False, log_file=None, log_dir="logs"):
    """
    Get a logger with the specified configuration
    
    Args:
        name (str): Logger name
        level (int): Logging level
        concise (bool): Use concise format for console output
        file (bool): Enable file logging
        log_file (str): Log file name
        log_dir (str): Directory for log files
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Set level
    logger.setLevel(level)
    
    # Create formatters
    if concise:
        console_format = '%(levelname)s: %(message)s'
    else:
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if requested
    if file:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if log_file is None:
            log_file = f"{name.replace('.', '_')}.log"
        
        file_path = os.path.join(log_dir, log_file)
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(file_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger
