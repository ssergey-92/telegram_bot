from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import BOT_COMMANDS


def create_help_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Function for making help reply keyboard consists of
    BOT_COMMAND shortcuts("Top Budget Hotels", "Top Luxury Hotels",
    "Custom Hotel Search", "History").

    :return: help reply Keyboard
    :rtype: ReplyKeyboardMarkup
    """

    reply_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    for index in range(3, len(BOT_COMMANDS)):
        reply_keyboard.add(
            KeyboardButton(
                text=BOT_COMMANDS[index][1]
            )
        )
    return reply_keyboard


help_reply_keyboard = create_help_reply_keyboard()
