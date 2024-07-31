"""Module for handling confirm_city state.

Contains common handling functions to handle confirm city from callback and
message for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from datetime import date
from typing import Union

from telebot.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telebot.handler_backends import State

from .search_min_price import min_allowed_min_price
from handlers.messages.utils.state_data import StateData
from keyboards.inline.calender.keyboards import (
    get_current_calendar_days_keyboard,
)
from keyboards.inline.search_cities import get_search_city_inline_keyboard
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger
from states.custom_search import CustomSearchStates

msg_select_city = "Kindly select one of the below options!"
msg_select_checkin = (
    "Select check in date:\n(ex. {current_date})"
)
msg_type_city = "Type city name:"
msg_set_min_price = (
    "Type minimum hotel price per day in USD:\n(ex. min: {min_price})"
    "\n*USD - United States dollar.".format(min_price=min_allowed_min_price)
)
msg_select_other_city = "Type another city"


def handle_confirm_city_from_msg(chat_id: int, user_id: int) -> None:
    """Handle user input data for confirming search city from message.

    Send suggested cities list to confirm from cities inline keyboard.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    cities_data = StateData.get_user_data_by_key(
        chat_id, user_id, "found_cities",
    )
    reply_markup = get_search_city_inline_keyboard(cities_data)
    bot.send_message(chat_id, msg_select_city, reply_markup=reply_markup)


def get_next_state_reply_data(
        state: State,
) -> tuple[str, Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]:
    """Return reply msg text and reply markup as per state.

    Args:
        state (State): next search state

    Returns:
        tuple[str, Union[ReplyKeyboardMarkup, InlineKeyboardMarkup]]: reply
            msg text and markup

    """
    if state == CustomSearchStates.min_price:
        reply_msg = msg_set_min_price
        reply_markup = cancel_reply_keyboard
    else:
        reply_msg = msg_select_checkin.format(
            current_date=date.today().strftime("%d.%m.%Y"),
        )
        reply_markup = get_current_calendar_days_keyboard()
    bot_logger.debug(f"{state=}, {reply_markup=}, {reply_msg=}")
    return reply_msg, reply_markup


def handle_confirm_city_from_callback(
        call: CallbackQuery, previous_state: State, next_state: State,
) -> None:
    """Handle confirm search city from callback.

    If user input city name == "Type another city" set previous state and
    send message for previous state.
    Else save data in bot state storage, set next state and send message for
    next state.

    Args:
        call (CallbackQuery): callback query
        previous_state (State): previous search state
        next_state (State): next search state

    """
    bot_logger.debug(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    if call.data == msg_select_other_city:
        bot.set_state(call.from_user.id, previous_state, call.message.chat.id)
        reply_msg = msg_type_city
        reply_markup = cancel_reply_keyboard
    else:
        cities_data = StateData.get_user_data_by_key(
            call.message.chat.id, call.from_user.id, "found_cities",
        )
        confirmed_city = cities_data[int(call.data)]
        bot.set_state(call.from_user.id, next_state, call.message.chat.id)
        StateData.save_multiple_user_data(
            call.message.chat.id, call.from_user.id, confirmed_city,
        )
        reply_msg, reply_markup = get_next_state_reply_data(next_state)
    bot_logger.debug(
        f"{call.message.chat.id=}, {call.from_user.id=}, {reply_msg=}"
    )
    bot.send_message(
        call.message.chat.id, reply_msg, reply_markup=reply_markup,
    )
