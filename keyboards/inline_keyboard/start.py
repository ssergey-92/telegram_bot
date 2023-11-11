from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data.config import BOT_COMMANDS


def create_start_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Making start inline keyboard consists of BOT_COMMAND shortcuts
    except "Cancel Current Search"  and "Start Bot" shortcut.

    :return: start_inline_keyboard
    :rtype: InlineKeyboardMarkup
    """

    start_inline_keyboard = InlineKeyboardMarkup(row_width=2)
    for index in range(2, len(BOT_COMMANDS)):
        start_inline_keyboard.add(InlineKeyboardButton(
            text=BOT_COMMANDS[index][1],
            callback_data=BOT_COMMANDS[index][0])
        )
    return start_inline_keyboard


start_inline_keyboard = create_start_inline_keyboard()
