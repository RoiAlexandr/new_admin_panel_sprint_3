import logging
import os

import dotenv

dotenv.load_dotenv()

_log_format = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"


def get_file_handler() -> logging.FileHandler:
    file_handler = logging.FileHandler('load_data.log')
    file_handler.setLevel(os.environ.get('LOGGING_1'))
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler() -> logging.StreamHandler:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(os.environ.get('LOGGING_2'))
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get('LOGGING_2'))
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
