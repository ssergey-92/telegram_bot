"""Module for handling hotel_amount.

Contains common handling functions to handle hotels amount to display
from message for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from telebot.handler_backends import State

from .common import get_int_number
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

min_hotels_amount = 1
max_hotels_amount = 3
msg_select_hotel_photos = "Do you need photo of hotels?\nType 'yes' or 'no'."
msg_use_digits = "Use digits to set hotels amount!\n(ex. 3)"
msg_min_hotels_amount = (
    "Min number of hotels to display is {min_hotels_amount}!"
    "\n(ex. {min_hotels_amount})".format(min_hotels_amount=min_hotels_amount)
)
msg_max_hotels_amount = (
    "Max number of hotels to display is {max_hotels_amount}!"
    "\n(ex. {max_hotels_amount})".format(max_hotels_amount=max_hotels_amount)
)


def handle_hotels_amount(
        chat_id: int, user_id: int, hotels_amount: str, next_state: State
) -> None:
    """Handle user input data for setting hotels amount to display.

    If hotels_amount as per format digit[min_hotels_amount:max_hotels_amount],
    save data into bot state storage, set next state(next_state) and send
    message for next state.
    Other vice send  message  with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        hotels_amount (str): hotels amount to display
        next_state (State): next search state

    """
    bot_logger.debug(
        f"{chat_id=}, {user_id=}, {hotels_amount=}, {next_state=}"
    )
    hotels_amount = get_int_number(hotels_amount)
    if not hotels_amount and hotels_amount != 0:
        reply_msg = msg_use_digits
    elif hotels_amount > max_hotels_amount:
        reply_msg = msg_max_hotels_amount
    elif hotels_amount < min_hotels_amount:
        reply_msg = msg_min_hotels_amount
    else:
        reply_msg = msg_select_hotel_photos
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "hotels_amount", hotels_amount,
        )
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
