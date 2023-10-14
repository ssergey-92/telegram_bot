from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data.config import BOT_COMMANDS


def create_search_city_inline_keyboard(sorted_data: list[dict]) \
        -> InlineKeyboardMarkup:
    city_inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for index in range(len(sorted_data)):
        city_inline_keyboard.add(InlineKeyboardButton(
            text=sorted_data[index]['fullName'],
            callback_data=str(index))
        )
    city_inline_keyboard.add(InlineKeyboardButton(
        text="Type another city:",
        callback_data="Type another city:")
    )
    return city_inline_keyboard



