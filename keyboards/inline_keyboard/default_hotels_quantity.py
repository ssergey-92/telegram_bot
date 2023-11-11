from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def default_hotels_quantity_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Making inline keyboard with hotels quantity = 10.

    :return:hotel_quantity_inline_keyboard
    :rtype: InlineKeyboardMarkup
    """

    hotel_quantity_inline_keyboard = InlineKeyboardMarkup(row_width=2)
    hotel_quantity_inline_keyboard.add(InlineKeyboardButton(
        text='10',
        callback_data='default_hotels_quantity')
    )
    return hotel_quantity_inline_keyboard


hotels_quantity_inline_keyboard = default_hotels_quantity_inline_keyboard()
