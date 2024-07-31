"""Module for handling travellers_amount state.

Contains common handling functions to handle travellers amount from message
for CustomSearchStates, LuxurySearchStates and BudgetSearchStates scenarios.
"""

from telebot.handler_backends import State

from .common import get_int_number
from .search_hotels_amount import max_hotels_amount, min_hotels_amount
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

min_travellers = 1
max_travellers = 14
msg_use_digits = (
    "Use digits to set number of travellers!\n(ex. min: {min_travellers}, "
    "max: {max_travellers})".format(
        min_travellers=min_travellers, max_travellers=max_travellers,
    )
)
msg_min_travellers = (
    "Min number of travellers is {min_travellers}!"
    "\n(ex. {min_travellers})".format(min_travellers=min_travellers)
)
msg_max_travellers = (
    "Max number of travellers is {max_travellers}!"
    "\n(ex. {max_travellers})".format(max_travellers=max_travellers)
)
msg_select_hotels_amount = (
    "How many hotels to display?\n(ex. min: {min_hotels}, max: "
    "{max_hotels})".format(
        min_hotels=min_hotels_amount, max_hotels=max_hotels_amount,
    )
)


def handle_travellers(
    chat_id: int, user_id: int, total_travellers: str, next_state: State,
) -> None:
    """Handle user input data for setting number of travellers.

    If user input number of travellers as per format digit
    [min_travellers:max_travellers], sav data into bot state storage, set
    next state and send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        total_travellers (str): number of travellers/guests
        next_state (State): next state

    """
    bot_logger.debug(
        f"{chat_id=}, {user_id=}, {total_travellers=}, {next_state=}"
    )
    total_travellers = get_int_number(total_travellers)
    if not total_travellers and total_travellers != 0:
        reply_msg = msg_use_digits
    elif total_travellers > max_travellers:
        reply_msg = msg_max_travellers
    elif total_travellers < min_travellers:
        reply_msg = msg_min_travellers
    else:
        reply_msg = msg_select_hotels_amount
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "adults", total_travellers,
        )
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
