"""Module for creating help reply keyboard"""

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import BOT_COMMANDS


def create_help_reply_keyboard() -> ReplyKeyboardMarkup:
    """Create help reply keyboard.

    It contains bot commands: beast deal, high price, low price and history.

    Returns:
        ReplyKeyboardMarkup: help reply Keyboard

    """
    reply_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    for cmd_category, commands in BOT_COMMANDS.items():
        if cmd_category == "main":
            continue
        for i_command in commands:
            reply_keyboard.add(KeyboardButton(i_command["shortcut"]))

    return reply_keyboard


help_reply_keyboard = create_help_reply_keyboard()
