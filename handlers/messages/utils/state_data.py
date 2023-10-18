from typing import Union, Any
from abc import ABC
from loader import bot


class StateData(ABC):
    @staticmethod
    def save_state_data_by_key(chat_id: int, user_id: int, key: str,
                               value: Union[str, dict, int, list]) -> None:
        with bot.retrieve_data(user_id, chat_id) as data:
            data[key] = value

    @staticmethod
    def save_multiple_data(chat_id: int, user_id: int, data_dict: dict) -> None:
        with bot.retrieve_data(user_id, chat_id) as data:
            for i_key, i_value in data_dict.items():
                data[i_key] = i_value


    @staticmethod
    def retrieve_data_by_key(chat_id: int, user_id: int, key: str) -> Any:
        with bot.retrieve_data(user_id, chat_id) as data:
            value = data[key]
        return value

    @staticmethod
    def retrieve_full_data_by_id(chat_id: int, user_id: int) -> dict:
        with bot.retrieve_data(user_id, chat_id) as data:
            full_user_data = data
        return full_user_data

    @staticmethod
    def delete_state(chat_id: int, user_id: int) -> None:
        try:
            bot.delete_state(user_id=user_id,
                             chat_id=chat_id
                             )
        except Exception as exc:
            print(type(exc))
