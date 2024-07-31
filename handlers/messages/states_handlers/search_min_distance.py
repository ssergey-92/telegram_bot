"""Module for handling min_distance state for CustomSearchStates scenarios."""

from telebot.handler_backends import State

from .common import get_int_number
from .search_max_distance import max_allowed_max_distance
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_use_digits = (
    "Use digits only to set min distance from cite center!\n(ex. 1)"
)
msg_type_max_distance = (
    "Type maximum hotel distance in miles from city center."
    "\n(ex. max: {max_distance})".format(max_distance=max_allowed_max_distance)
)
max_allowed_min_distance = 200
msg_max_allowed_min_distance = (
    "Maximum distance from cite center is {max_distance}!"
    "\n(ex. {max_distance})".format(max_distance=max_allowed_min_distance)
)
min_allowed_min_distance = 0
msg_min_allowed_min_distance = (
    "Min allowed distance from cite center is {min_distance}!"
    "\n(ex. {min_distance})".format(min_distance=min_allowed_min_distance)
)


def handle_min_distance(
    chat_id: int, user_id: int, min_distance: str, next_state: State
) -> None:
    """Handle user data for setting minimum hotel distance from city center.

    If user input min hotel distance from city center as per format digit
    [min_allowed_min_distance, max_allowed_min_distance], then save data into
    bot state storage, set next state and send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        min_distance (str): min distance from city center
        next_state (State): next state

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {min_distance=}, {next_state=}")
    min_distance = get_int_number(min_distance)
    if not min_distance and min_distance != 0:
        reply_msg = msg_use_digits
    elif min_distance < min_allowed_min_distance:
        reply_msg = msg_min_allowed_min_distance
    elif min_distance > max_allowed_min_distance:
        reply_msg = msg_max_allowed_min_distance
    else:
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "min_distance", min_distance,
        )
        reply_msg = msg_type_max_distance
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
