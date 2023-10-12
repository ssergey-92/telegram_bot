from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import BOT_COMMANDS


def create_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    reply_keyboard = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        row_width=1
    )
    reply_keyboard.add(KeyboardButton(text=BOT_COMMANDS[1][1]))
    return reply_keyboard


cancel_reply_keyboard = create_cancel_reply_keyboard()