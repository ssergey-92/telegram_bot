"""Module for catching and handling each state in BudgetSearchStates."""

from telebot.types import Message, CallbackQuery

from .states_handlers.search_check_in_date import (
    handle_check_in_date_from_callback,
    handle_check_in_date_from_message,
)
from .states_handlers.search_check_out_date import (
    handle_check_out_date_from_callback,
    handle_check_out_date_from_message,
)
from .states_handlers.search_confirm_city import (
    handle_confirm_city_from_msg,
    handle_confirm_city_from_callback,
)
from .states_handlers.search_input_city import handle_input_city
from .states_handlers.search_hotels_amount import handle_hotels_amount
from .states_handlers.search_hotel_photos_amount import (
    handle_hotel_photos_amount,
)
from .states_handlers.search_hotels_photos_display import (
    handle_hotel_photos_display
)
from .states_handlers.search_trevellers import handle_travellers
from loader import bot
from project_logging.bot_logger import bot_logger
from states.budget_search import BudgetSearchStates


@bot.message_handler(state=BudgetSearchStates.input_city)
def input_city_state(message: Message) -> None:
    """Get state: BudgetSearchStates.input_city and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_input_city(
        message.chat.id,
        message.from_user.id,
        message.text,
        BudgetSearchStates.confirm_city,
    )


@bot.callback_query_handler(
    func=lambda call: call, state=BudgetSearchStates.confirm_city,
)
def confirm_city_state_from_callback(call: CallbackQuery):
    """Get state: BudgetSearchStates.confirm_city from callback.

    Call handling function.

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_confirm_city_from_callback(
        call, BudgetSearchStates.input_city, BudgetSearchStates.check_in_date,
    )


@bot.message_handler(state=BudgetSearchStates.confirm_city)
def confirm_city_state_from_message(message: Message) -> None:
    """Get state: BudgetSearchStates.confirm_city from message.

    Call handling function. City can be confirmed only from inline keyboard.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_confirm_city_from_msg(message.chat.id, message.from_user.id)


@bot.callback_query_handler(
    func=lambda call: call, state=BudgetSearchStates.check_in_date,
)
def check_in_date_state_from_callback(call: CallbackQuery) -> None:
    """Get state: BudgetSearchStates.check_in_date from calendar keyboard.

    Call handling function.
    To be initialized after func calendar_action_handler and
    calendar_zoom_out_handler for handling them first!

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_check_in_date_from_callback(call, BudgetSearchStates.check_out_date)


@bot.message_handler(state=BudgetSearchStates.check_in_date)
def check_in_date_state_from_state_message(message: Message) -> None:
    """Get state: BudgetSearchStates.check_in_date from message.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_check_in_date_from_message(
        message, BudgetSearchStates.check_out_date,
    )


@bot.callback_query_handler(
    func=lambda call: call, state=BudgetSearchStates.check_out_date
)
def check_out_date_state_from_callback(call: CallbackQuery) -> None:
    """Get state: BudgetSearchStates.check_out_date from calendar keyboard.

    Call handling function.

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_check_out_date_from_callback(
        call, BudgetSearchStates.travellers_amount,
    )


@bot.message_handler(state=BudgetSearchStates.check_out_date)
def check_out_date_state_from_message(message: Message) -> None:
    """Get state: BudgetSearchStates.check_out_date from message.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_check_out_date_from_message(
        message, BudgetSearchStates.travellers_amount,
    )


@bot.message_handler(state=BudgetSearchStates.travellers_amount)
def travellers_state(message: Message) -> None:
    """Get state: BudgetSearchStates.travellers_amount and call handling func.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_travellers(
        message.chat.id,
        message.from_user.id,
        message.text,
        BudgetSearchStates.hotels_amount,
    )


@bot.message_handler(state=BudgetSearchStates.hotels_amount)
def hotels_amount_state(message: Message) -> None:
    """Get state: BudgetSearchStates.hotels_amount and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_hotels_amount(
        message.chat.id,
        message.from_user.id,
        message.text,
        BudgetSearchStates.hotels_photos_display,
    )


@bot.message_handler(state=BudgetSearchStates.hotels_photos_display)
def photo_state(message: Message) -> None:
    """Get state: BudgetSearchStates.hotels_photos_display.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_hotel_photos_display(
        message.chat.id,
        message.from_user.id,
        message.text,
        BudgetSearchStates.hotel_photos_amount,
    )


@bot.message_handler(state=BudgetSearchStates.hotel_photos_amount)
def photo_amount_state(message: Message) -> None:
    """Get state: BudgetSearchStates.hotel_photos_amount.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_hotel_photos_amount(
        message.chat.id, message.from_user.id, message.text,
    )
