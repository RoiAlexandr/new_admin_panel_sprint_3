import time
from functools import wraps

from utils.logger_util import get_logger

logger = get_logger(__name__)


def backoff(exceptions, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """Перезапускает функцию в ответ на исключения от нее"""

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.info(str(e))
                    logger.warning(str(e))
                    sleep_time = sleep_time * factor
                    if sleep_time > border_sleep_time:
                        sleep_time = border_sleep_time
                    time.sleep(sleep_time)

        return inner

    return func_wrapper
