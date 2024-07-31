"""Module for handling max_distance state for CustomSearchStates scenarios."""

from datetime import date

from telebot.handler_backends import State

from .common import get_int_number
from handlers.messages.utils.state_data import StateData
from keyboards.inline.calender.keyboards import (
    get_current_calendar_days_keyboard,
)
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_select_checkin = "Select check in date:\n(ex. {current_date})"
msg_use_digits = (
    "Use digits only to set max distance from cite center!\n(ex. 20)"
)
max_allowed_max_distance = 300
msg_max_allowed_max_distance = (
    "Maximum distance from cite center is {max_distance}!"
    "\n(ex. {max_distance})".format(max_distance=max_allowed_max_distance)
)
msg_min_allowed_max_distance = (
    "Max distance must be greater then min distance: {min_distance}!"
)


def handle_max_distance(
        chat_id: int, user_id: int, max_distance: str, next_state: State,
) -> None:
    """Handle user data for setting maximum hotel distance from city center.

    If user input max hotel distance from city center as per format digit
    [min_distance, msg_max_allowed_max_distance], then data into bot state
    storage, set next state and send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        max_distance (str): max distance from city center
        next_state (State): next state

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {max_distance=}, {next_state=}")
    max_distance = get_int_number(max_distance)
    min_distance = StateData.get_user_data_by_key(
        chat_id, user_id, "min_distance",
    )
    reply_markup = cancel_reply_keyboard
    if not max_distance and max_distance != 0:
        reply_msg = msg_use_digits
    elif max_distance > max_allowed_max_distance:
        reply_msg = msg_max_allowed_max_distance
    elif max_distance <= min_distance:
        reply_msg = msg_min_allowed_max_distance.format(
            min_distance=min_distance,
        )
    else:
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "max_distance", max_distance,
        )
        reply_msg = msg_select_checkin.format(
            current_date=date.today().strftime("%d.%m.%Y")
        )
        reply_markup = get_current_calendar_days_keyboard()
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=reply_markup)
