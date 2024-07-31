"""Module for handling check_in_date state.

Contains common handling functions to handle check in date from message and
callback for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from datetime import date

from telebot.handler_backends import StatesGroup, State
from telebot.types import Message, CallbackQuery

from .common import (
    check_date_format,
    convert_date_from_str_to_dict,
    extract_date_from_callback,
    get_next_day_date,
    send_calendar_callback_error_msg,
    send_invalid_format_date_msg,
)
from handlers.messages.utils.state_data import StateData
from keyboards.inline.calender.keyboards import (
    get_current_calendar_days_keyboard,
)
from loader import bot
from project_logging.bot_logger import bot_logger

msg_select_checkout = "Select check out date:\n(ex. {next_date})"
msg_select_valid_checkin = "Select check in date starting {current_date}:"


def handle_check_in_date_from_message(
        message: Message, next_state: State,
) -> None:
    """Handle check in date from message.

    If check in date format is valid then call handler for check in date.
    Other vice call func for sending corrective actions.

    Args:
        message (Message): user reply data.
        next_state (State): next search state.

    """
    bot_logger.debug(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    error_msg = check_date_format(message.text)
    if error_msg:
        send_invalid_format_date_msg(error_msg, message.chat.id)
    else:
        check_in_date = convert_date_from_str_to_dict(message.text)
        set_check_in_date(
            message.chat.id, message.from_user.id, check_in_date, next_state,
        )


def handle_check_in_date_from_callback(
        call: CallbackQuery, next_state: State,
) -> None:
    """Handle check in date from callback of inline calendar keyboard.

    If selected date on calendar, then call handle func for check in date.
    Other vice call func for sending corrective actions.

    Args:
        call (CallbackQuery): user reply data
        next_state (State): next search state

    """
    bot_logger.debug(f"{call.message.chat.id=}, {call.from_user.id=}, {call=}")
    check_in_date = extract_date_from_callback(call)
    if not check_in_date:
        send_calendar_callback_error_msg(call.message.chat.id)
    else:
        set_check_in_date(
            call.message.chat.id, call.from_user.id, check_in_date, next_state,
        )


def set_check_in_date(
    chat_id: int, user_id: int, check_in_date: dict, next_state: State,
) -> None:
    """Handle logic for setting check in date.

    If check in date is valid then save it into bot state storage, set
    new state(CustomSearchStates.check_out_date) send message for next state.
    Other vice bot send  message  with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        check_in_date (dict): check in date in hotel
        next_state (State): next search state

    """
    bot_logger.debug(
        f"{chat_id=}, {user_id=}, {check_in_date=}, {next_state=}"
    )
    reply_markup = get_current_calendar_days_keyboard()
    if valid_check_in_date(check_in_date):
        next_day_date = get_next_day_date(check_in_date)
        reply_msg = msg_select_checkout.format(
            next_date=next_day_date
        )
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "check_in_date", check_in_date,
        )
    else:
        reply_msg = msg_select_valid_checkin.format(
            current_date=date.today().strftime("%d.%m.%Y"),
        )
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=reply_markup)


def valid_check_in_date(check_in_date: dict) -> bool:
    """Check if check in date >= current date.

    Args:
        check_in_date (dict): check in date

    Returns:
        bool: True if check in date >= current date, else False

    """
    converted_date = date(
        check_in_date["year"], check_in_date["month"], check_in_date["day"],
    )
    current_date = date.today()
    bot_logger.debug(f"{check_in_date=}, {current_date=}")
    return converted_date >= current_date
