"""Module for creating cities inline keyboard"""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_search_city_inline_keyboard(
    found_cities: list[dict],
) -> InlineKeyboardMarkup:
    """Create inline keyboard with found cities names and "type another city".
    Args:
        found_cities (list[dict]): found cities data

    Returns:
        InlineKeyboardMarkup: city_inline_keyboard

    """
    city_inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for index in range(len(found_cities)):
        city_inline_keyboard.add(
            InlineKeyboardButton(
                text=found_cities[index]["full_name"], callback_data=str(index)
            )
        )
    city_inline_keyboard.add(
        InlineKeyboardButton(
            text="Type another city:", callback_data="Type another city"
        )
    )
    return city_inline_keyboard
