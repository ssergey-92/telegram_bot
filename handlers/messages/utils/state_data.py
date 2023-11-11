from abc import ABC
from typing import Union, Any, Optional

from loader import bot


class StateData(ABC):
    """
    Base class StateData. Parent Class (abc.ABC)
    Class for handling user state data
    """

    @staticmethod
    def save_state_data_by_key(chat_id: int, user_id: int, key: str,
                               value: Union[str, dict, int, list]) -> None:
        """
        Saving single user state data in user specific dict.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param key: name of key for saving value
        :type key: str
        :param value: data to save
        :type value: Union[str, dict, int, list]
        """

        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                data[key] = value
        except KeyError as exc:
            print(exc)

    @staticmethod
    def save_multiple_data(chat_id: int, user_id: int, data_dict: dict) -> None:
        """
        Saving multiple user state data in user specific dict.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param data_dict:
        :type data_dict: dict
        """

        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                for i_key, i_value in data_dict.items():
                    data[i_key] = i_value
        except KeyError as exc:
            print(exc)

    @staticmethod
    def retrieve_data_by_key(chat_id: int, user_id: int, key: str) \
            -> Optional[Any]:
        """
        Retrieving single user state data by key in user specific dict.
        If key is not exists, return None.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param key: name of key for retrieving data
        :type key: str

        :return: value of key
        :rtype: Any
        """

        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                value = data[key]
        except KeyError as exc:
            value = None
        return value

    @staticmethod
    def retrieve_full_data_by_id(chat_id: int, user_id: int) -> dict:
        """
        Retrieving full user state data from user specific dict.
        If user state data is not exists, return None.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int

        :return: full user state data
        :rtype: Any
        """

        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                full_user_data = data
        except KeyError as exc:
            full_user_data = None
        return full_user_data

    @staticmethod
    def delete_state(chat_id: int, user_id: int) -> None:
        """
        Deleting user state data from user specific dict.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        """

        try:
            bot.delete_state(user_id=user_id,
                             chat_id=chat_id
                             )
        except Exception as exc:
            print(f"Delete user state exception: {type(exc)}")
