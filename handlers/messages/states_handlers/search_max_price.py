"""Module for handling max_price state for CustomSearchStates scenarios."""

from telebot.handler_backends import State

from .common import get_int_number
from .search_min_distance import min_allowed_min_distance
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_set_min_distance = (
    "Type minimum hotel distance in miles from city center."
    "\n(ex. min: {min_distance})".format(min_distance=min_allowed_min_distance)
)
msg_use_digits = "Use digits only to set max price!!\n(ex. 1000)"
msg_min_allowed_max_price = (
    "Max price must be higher then min price: {min_price} USD."
)
max_allowed_max_price = 1000000
msg_max_allowed_max_price = (
    "Maximum price per day is {max_price} USD!\n(ex. {max_price})".format(
        max_price=max_allowed_max_price,
    )
)


def handle_max_price(
        chat_id: int, user_id: int, max_price: str, next_state: State,
) -> None:
    """Handle user input data for setting maximum hotel price per day.

    If user input max hotel price per day as per format digit
    [min_price, max_allowed_max_price] then save data in bot state storage, set
    next state and send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        max_price (str): max hotel price per day
        next_state (State): next state

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {max_price=}, {next_state=}")
    max_price = get_int_number(max_price)
    min_price = StateData.get_user_data_by_key(chat_id, user_id, "min_price")
    if not max_price and max_price != 0:
        reply_msg = msg_use_digits
    elif max_price <= min_price:
        reply_msg = msg_min_allowed_max_price.format(min_price=min_price)
    elif max_price > max_allowed_max_price:
        reply_msg = msg_max_allowed_max_price
    else:
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "max_price", max_price,
        )
        reply_msg = msg_set_min_distance
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
