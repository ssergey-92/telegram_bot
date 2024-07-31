"""Module for handling check_out_date state.

Contains common handling functions to handle check out date from message and
callback for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from datetime import datetime

from telebot.handler_backends import State
from telebot.types import Message, CallbackQuery

from .common import (
    check_date_format,
    convert_date_from_str_to_dict,
    extract_date_from_callback,
    get_next_day_date,
    send_calendar_callback_error_msg,
    send_invalid_format_date_msg,
)
from .search_trevellers import min_travellers, max_travellers
from handlers.messages.utils.state_data import StateData
from keyboards.inline.calender.keyboards import (
    get_current_calendar_days_keyboard,
)
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_input_travellers = (
    "Type number of travellers: \n(ex. min: {min_travellers}, "
    "max: {max_travellers})".format(
        min_travellers=min_travellers, max_travellers=max_travellers,
    )
)
msg_select_checkout_after_checkin = (
    "Select check out date after check in date {next_day_date}"
)


def handle_check_out_date_from_message(
        message: Message, next_state: State,
) -> None:
    """Handle check out date from message.

    If date format is valid then call handler for check out date.
    Other vice call func for sending corrective actions.

    Args:
        message (Message): user reply data
        next_state (State): next search state

    """
    bot_logger.debug(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    error_msg = check_date_format(message.text)
    if error_msg:
        send_invalid_format_date_msg(error_msg, message.chat.id)
    else:
        check_out_date = convert_date_from_str_to_dict(message.text)
        set_check_out_date(
            message.chat.id, message.from_user.id, check_out_date, next_state,
        )


def handle_check_out_date_from_callback(
        call: CallbackQuery, next_state: State,
) -> None:
    """Handle check out date from callback of inline calendar keyboard.

    If selected date on calendar then call handle func for check out date.
    Other vice call func for sending corrective actions.

    Args:
        call (CallbackQuery): user reply data
        next_state (State): next search state

    """
    bot_logger.debug(f"{call.message.chat.id=}, {call.from_user.id=}, {call=}")
    check_out_date = extract_date_from_callback(call)
    if not check_out_date:
        send_calendar_callback_error_msg(call.message.chat.id)
    else:
        set_check_out_date(
            call.message.chat.id,
            call.from_user.id,
            check_out_date,
            next_state,
        )


def set_check_out_date(
    chat_id: int, user_id: int, check_out_date: dict, next_state: State,
) -> None:
    """Handle user date for setting check out date.

    If user input check out date is valid, save the above data into bot state
    storage, set next state(next_state) send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        check_out_date (dict): check out date in hotel
        next_state (State): next search state

    """
    bot_logger.debug(
        f"{chat_id=}, {user_id=}, {check_out_date=}, {next_state=}"
    )
    check_in_date = StateData.get_user_data_by_key(
        chat_id, user_id, "check_in_date",
    )
    if is_valid_check_out_date(check_in_date, check_out_date):
        reply_msg = msg_input_travellers
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "check_out_date", check_out_date
        )
        reply_markup = cancel_reply_keyboard
    else:
        next_day_date = get_next_day_date(check_in_date)
        reply_msg = msg_select_checkout_after_checkin.format(
            next_day_date=next_day_date,
            )
        reply_markup = get_current_calendar_days_keyboard()
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=reply_markup)


def is_valid_check_out_date(check_in_date: dict, check_out_date: dict) -> bool:
    """Check if check out date > check in date.

    Args:
        check_in_date (dict): check in date in hotel
        check_out_date (dict): check out date in hotel

    Returns:
        bool: True if check out date > check in date

    """
    bot_logger.debug(f"{check_in_date=}, {check_out_date=}")
    converted_check_in_date = datetime(
        check_in_date["year"], check_in_date["month"], check_in_date["day"],
    )
    converted_check_out_date = datetime(
        check_out_date["year"],
        check_out_date["month"],
        check_out_date["day"],
    )
    return converted_check_out_date > converted_check_in_date
