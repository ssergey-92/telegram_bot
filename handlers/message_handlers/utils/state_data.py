from typing import Union, Any

from loader import bot


def save_state_data(chart_id: int, user_id: int, title: str,
                    definition: Union[str, dict, int]) -> None:
    with bot.retrieve_data(user_id, chart_id) as data:
        data[title] = definition


def take_state_data(chart_id: int, user_id: int, title: str) -> Any:
    with bot.retrieve_data(user_id, chart_id) as data:
        data = data[title]
    return data


def delete_state(chat_id: int, user_id: int) -> None:
    try:
        bot.delete_state(user_id=user_id,
                         chat_id=chat_id
                         )
    except Exception as exc:
        print(type(exc))