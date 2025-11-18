"""Retry logic decorator for handling failures."""

import time
from functools import wraps
from utils.logger import logger
from typing import Callable


def retry_on_failure(max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry

    Usage:
        @retry_on_failure(max_retries=3, delay=2.0, backoff=2.0)
        def my_function():
            # Code that might fail
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}: {str(e)}"
                        )

            # If all retries failed, raise the last exception
            raise last_exception

        return wrapper
    return decorator
