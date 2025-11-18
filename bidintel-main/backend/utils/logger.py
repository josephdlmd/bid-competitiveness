"""Logging configuration using loguru."""

from loguru import logger
from config.settings import settings
import sys


def setup_logger():
    """Configure logger with file and console outputs."""

    # Remove default handler
    logger.remove()

    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # Add file handler
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip"  # Compress rotated logs
    )

    return logger


# Initialize logger
setup_logger()

# Export logger instance
__all__ = ['logger']
