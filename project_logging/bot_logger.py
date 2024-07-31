"""Module for creation project logger."""

from os import path as os_path, environ as os_environ
from pathlib import Path
from logging import DEBUG, Formatter, Logger, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler

logs_dir = os_path.abspath(os_path.join(
    os_path.dirname(os_path.realpath(__file__)), "logs")
)


def get_stream_handler() -> StreamHandler:
    """Create stream handler for logger.

    Returns:
        StreamHandler : stream handler

    """
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    formatter = Formatter(
        "*** %(asctime)s | %(name)s | %(levelname)s | %(module)s | "
        "%(funcName)s | %(message)s",
    )
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_rotating_file_handler(logs_file_path: str) -> RotatingFileHandler:
    """Create rotating file handler for logger.

    Args:
        logs_file_path (str): logs file saving abs path

    Returns:
        RotatingFileHandler : rotating file handler

    """
    rotating_file_handler = RotatingFileHandler(
        filename=logs_file_path,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8",
    )
    rotating_file_handler.setLevel(DEBUG)
    formatter = Formatter(
        "%(asctime)s|%(name)s|%(levelname)s|%(pathname)s|%(funcName)s|"
        "%(message)s",
    )
    rotating_file_handler.setFormatter(formatter)
    return rotating_file_handler


def create_logs_file_path() -> str:
    """Create and return logs abs path if it is not existed.

    Returns:
        str: abs path

    """
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    logs_file_path = os_path.join(logs_dir, os_environ.get("LOGS_FILE_NAME"))

    return logs_file_path


def create_project_logger(logger_name: str) -> Logger:
    """Create logger for project.

    Args:
        logger_name (str): name of logger

    Returns:
        Logger : instance of Logger

    """
    logger = getLogger(logger_name)
    logger.handlers.clear()
    logs_file_path = create_logs_file_path()
    for i_handler in (
            get_stream_handler(), get_rotating_file_handler(logs_file_path)
    ):
        logger.addHandler(i_handler)
    logger.setLevel(DEBUG)
    return logger


bot_logger = create_project_logger("bot_logger")
