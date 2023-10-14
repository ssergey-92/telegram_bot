from typing import Union, Any

from loader import bot


def save_state_data(chart_id: int, user_id: int, key: str,
                    value: Union[str, dict, int, list]) -> None:
    with bot.retrieve_data(user_id, chart_id) as data:
        data[key] = value


def take_state_data(chart_id: int, user_id: int, key: str) -> Any:
    with bot.retrieve_data(user_id, chart_id) as data:
        value = data[key]
    return value


def delete_state(chat_id: int, user_id: int) -> None:
    try:
        bot.delete_state(user_id=user_id,
                         chat_id=chat_id
                         )
    except Exception as exc:
        print(type(exc))

