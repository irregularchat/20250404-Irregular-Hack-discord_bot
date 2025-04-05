import logging

def get_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and level.
    If called multiple times, returns the same logger instance since
    logging.getLogger(name) always returns the same logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # If you don't want multiple handlers added each time, check first
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
