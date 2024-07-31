"""Module for catching and handling each state in CustomSearchStates."""

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
from .states_handlers.search_max_distance import handle_max_distance
from .states_handlers.search_max_price import handle_max_price
from .states_handlers.search_min_distance import handle_min_distance
from .states_handlers.search_min_price import handle_min_price
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
from states.custom_search import CustomSearchStates


@bot.message_handler(state=CustomSearchStates.input_city)
def input_city_state(message: Message) -> None:
    """Get state: CustomSearchStates.input_city and call handling function.

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
        CustomSearchStates.confirm_city,
    )


@bot.callback_query_handler(
    func=lambda call: call, state=CustomSearchStates.confirm_city,
)
def confirm_city_state_from_callback(call: CallbackQuery):
    """Get state: CustomSearchStates.confirm_city from callback.

    Call handling function.

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_confirm_city_from_callback(
        call, CustomSearchStates.input_city, CustomSearchStates.min_price,
    )


@bot.message_handler(state=CustomSearchStates.confirm_city)
def confirm_city_state_from_message(message: Message) -> None:
    """Get state: CustomSearchStates.confirm_city from message.

    Call handling function. City can be confirmed only from inline keyboard.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_confirm_city_from_msg(message.chat.id, message.from_user.id)


@bot.message_handler(state=CustomSearchStates.min_price)
def min_price_state(message: Message) -> None:
    """Get state: CustomSearchStates.min_price and call handling function.

    Args:
        message (Message): user reply data

    """

    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_min_price(
        message.chat.id,
        message.from_user.id,
        message.text,
        CustomSearchStates.max_price,
    )


@bot.message_handler(state=CustomSearchStates.max_price)
def max_price_state(message: Message) -> None:
    """Get state: CustomSearchStates.max_price and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_max_price(
        message.chat.id,
        message.from_user.id,
        message.text,
        CustomSearchStates.min_distance,
    )


@bot.message_handler(state=CustomSearchStates.min_distance)
def min_distance_state(message: Message) -> None:
    """Get state: CustomSearchStates.min_distance and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_min_distance(
        message.chat.id,
        message.from_user.id,
        message.text,
        CustomSearchStates.max_distance,
    )


@bot.message_handler(state=CustomSearchStates.max_distance)
def max_distance_state(message: Message) -> None:
    """Get state: CustomSearchStates.max_distance and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_max_distance(
        message.chat.id,
        message.from_user.id,
        message.text,
        CustomSearchStates.check_in_date,
    )


@bot.callback_query_handler(
    func=lambda call: call, state=CustomSearchStates.check_in_date,
)
def check_in_date_state_from_callback(call: CallbackQuery) -> None:
    """Get state: CustomSearchStates.check_in_date from calendar keyboard.

    Call handling function.
    To be initialized after func calendar_action_handler and
    calendar_zoom_out_handler for handling them first!

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_check_in_date_from_callback(call, CustomSearchStates.check_out_date)


@bot.message_handler(state=CustomSearchStates.check_in_date)
def check_in_date_state_from_state_message(message: Message) -> None:
    """Get state: CustomSearchStates.check_in_date from message.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_check_in_date_from_message(
        message, CustomSearchStates.check_out_date,
    )


@bot.callback_query_handler(
    func=lambda call: call, state=CustomSearchStates.check_out_date
)
def check_out_date_state_from_callback(call: CallbackQuery) -> None:
    """Get state: CustomSearchStates.check_out_date from calendar keyboard.

    Call handling function.

    Args:
        call (CallbackQuery): user reply data

    """
    bot_logger.info(
        f"{call.message.chat.id=}, {call.from_user.id=}, {call.data=}"
    )
    handle_check_out_date_from_callback(
        call, CustomSearchStates.travellers_amount,
    )


@bot.message_handler(state=CustomSearchStates.check_out_date)
def check_out_date_state_from_message(message: Message) -> None:
    """Get state: CustomSearchStates.check_out_date from message.

    Call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_check_out_date_from_message(
        message, CustomSearchStates.travellers_amount,
    )


@bot.message_handler(state=CustomSearchStates.travellers_amount)
def travellers_state(message: Message) -> None:
    """Get state: CustomSearchStates.travellers_amount and call handling func.

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
        CustomSearchStates.hotels_amount,
    )


@bot.message_handler(state=CustomSearchStates.hotels_amount)
def hotels_amount_state(message: Message) -> None:
    """Get state: CustomSearchStates.hotels_amount and call handling function.

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
        CustomSearchStates.hotels_photos_display,
    )


@bot.message_handler(state=CustomSearchStates.hotels_photos_display)
def photo_state(message: Message) -> None:
    """Get state: CustomSearchStates.hotels_photos_display.

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
        CustomSearchStates.hotel_photos_amount,
    )


@bot.message_handler(state=CustomSearchStates.hotel_photos_amount)
def photo_amount_state(message: Message) -> None:
    """Get state: CustomSearchStates.hotel_photos_amount.

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
