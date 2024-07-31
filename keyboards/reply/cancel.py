"""Module for creating cancel reply keyboard"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import CANSEL_SEARCH_COMMAND_DATA


def create_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """Create cancel reply keyboard with shortcut for command "cansel search".

    Returns:
        ReplyKeyboardMarkup: cancel reply Keyboard

    """
    reply_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    reply_keyboard.add(KeyboardButton(CANSEL_SEARCH_COMMAND_DATA["shortcut"]))
    return reply_keyboard


cancel_reply_keyboard = create_cancel_reply_keyboard()
