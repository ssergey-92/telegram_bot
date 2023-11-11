from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import BOT_COMMANDS


def create_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Function for making cancel reply keyboard consists of BOT_COMMAND
    "Cancel Current Search" shortcut.

    :return: cancel reply Keyboard
    :rtype: ReplyKeyboardMarkup
    """

    reply_keyboard = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        row_width=1
    )
    reply_keyboard.add(KeyboardButton(text=BOT_COMMANDS[1][1]))
    return reply_keyboard


cancel_reply_keyboard = create_cancel_reply_keyboard()
