"""Module for saving state data and deleting state."""

from typing import Any, Optional

from loader import bot
from project_logging.bot_logger import bot_logger


class StateData:
    """
    Base class StateData. Parent Class (abc.ABC)
    Class for handling user state and data.
    """
    @staticmethod
    def save_single_user_data(
        chat_id: int, user_id: int, key: str, value: Any,
    ) -> None:
        """Save single user data {key:value} in bot state storage.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier
            key (str): name of key for saving data
            value (Any): data to save

        """
        bot_logger.debug(f"{key=}, {value=}, {chat_id=}, {user_id=}")
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                data[key] = value
        except (KeyError, TypeError, ValueError) as exc:
            bot_logger.error(f"{exc=}, {chat_id=}, {user_id=}")

    @staticmethod
    def save_multiple_user_data(
        chat_id: int, user_id: int, save_data: dict
    ) -> None:
        """Save multiple user data in bot state storage.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier
            save_data (dict): data to save

        """
        bot_logger.debug(f"{chat_id=}, {user_id=}, {save_data=}")
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                for i_key, i_value in save_data.items():
                    data[i_key] = i_value
        except (KeyError, TypeError, ValueError) as exc:
            bot_logger.error(f"{exc=}, {chat_id=}, {user_id=}")

    @staticmethod
    def get_user_data_by_key(
        chat_id: int, user_id: int, key: str
    ) -> Optional[Any]:
        """Get single user data by key from bot state storage.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier
            key (str): name of key for getting data

        Returns:
            Any: value of the key

        """
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                value = data[key]
                bot_logger.debug(f" {key=}, {value=}, {chat_id=}, {user_id=}")
        except (KeyError, TypeError, ValueError) as exc:
            bot_logger.error(f"{exc=}, {chat_id=}, {user_id=}")
            value = None
        return value

    @staticmethod
    def get_full_user_data(chat_id: int, user_id: int) -> Optional[dict]:
        """Retrieve full user data from bot state storage.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier

        Returns:
            Optional[dict]: full user state data

        """
        with bot.retrieve_data(user_id, chat_id) as data:
            full_user_data = data
        bot_logger.debug(f"{full_user_data=}, {chat_id=}, {user_id=}")
        return full_user_data

    @staticmethod
    def delete_state(chat_id: int, user_id: int) -> None:
        """Delete user state and its data from bot state storage.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier

        """
        bot_logger.debug(f"{chat_id=}, {user_id=}")
        try:
            bot.delete_state(user_id=user_id, chat_id=chat_id)
        except Exception as exc:
            bot_logger.error(f"{exc=}, {chat_id=}, {user_id=}")
