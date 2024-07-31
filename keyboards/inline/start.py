"""Module for creating start inline keyboard"""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data.config import (
    BOT_COMMANDS,
    CANSEL_SEARCH_COMMAND_DATA,
    START_COMMAND_DATA,
)


def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Create start inline keyboard.

    Include all BOT_COMMAND shortcuts except "Cancel Current Search" and
    "Start Bot".

    Returns:
        InlineKeyboardMarkup: start inline keyboard

    """
    start_keyboard = InlineKeyboardMarkup(row_width=2)
    for commands in BOT_COMMANDS.values():
        for i_command in commands:
            if i_command in (START_COMMAND_DATA, CANSEL_SEARCH_COMMAND_DATA):
                continue
            start_keyboard.add(InlineKeyboardButton(
                text=i_command["shortcut"],
                callback_data=i_command["command"],
                )
            )
    return start_keyboard


start_inline_keyboard = get_start_inline_keyboard()
