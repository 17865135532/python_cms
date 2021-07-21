import functools
import time
import logging

logger = logging.getLogger(__name__)


def clock(log_level=logging.DEBUG):
    """this is outer clock function"""

    def clocked(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            """this is inner clocked function"""
            start_time = time.time()
            result = func(*args, **kwargs)
            time_cost = time.time() - start_time
            logger.log(msg=f"{func.__name__} func time_cost -> {time_cost}", level=log_level)
            return result
        return inner
    return clocked
