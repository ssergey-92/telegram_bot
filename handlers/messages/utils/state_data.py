from typing import Union, Any
from abc import ABC
from loader import bot


class StateData(ABC):
    @staticmethod
    def save_state_data_by_key(chat_id: int, user_id: int, key: str,
                               value: Union[str, dict, int, list]) -> None:
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                data[key] = value
        except KeyError as exc:
            print(exc)

    @staticmethod
    def save_multiple_data(chat_id: int, user_id: int, data_dict: dict) -> None:
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                for i_key, i_value in data_dict.items():
                    data[i_key] = i_value
        except KeyError as exc:
            print(exc)

    @staticmethod
    def retrieve_data_by_key(chat_id: int, user_id: int, key: str) -> Any:
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                value = data[key]
        except KeyError as exc:
            value = None
        return value

    @staticmethod
    def retrieve_full_data_by_id(chat_id: int, user_id: int) -> dict:
        try:
            with bot.retrieve_data(user_id, chat_id) as data:
                full_user_data = data
        except KeyError as exc:
            full_user_data = None
        return full_user_data

    @staticmethod
    def delete_state(chat_id: int, user_id: int) -> None:
        try:
            bot.delete_state(user_id=user_id,
                             chat_id=chat_id
                             )
        except Exception as exc:
            print(type(exc))
