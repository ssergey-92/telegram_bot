from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def default_hotels_quantity_inline_keyboard() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(InlineKeyboardButton(
            text='10',
            callback_data='default_hotels_quantity')
        )
    return inline_keyboard


hotels_quantity_inline_keyboard = default_hotels_quantity_inline_keyboard()