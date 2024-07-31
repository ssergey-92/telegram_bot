"""Module for handling hotel_photos_amount.

Contains common handling functions to handle hotels photo amount to display
from message for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from typing import Optional

from .common import get_int_number
from .search_result import handle_hotel_search
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

min_hotel_photos_amount = 1
max_hotel_photos_amount = 5
msg_searching_hotels = (
    "Kindly wait, searching for your suitable hotels.\n"
    "*press cancel button if your want to break the search."
)
msg_use_digits = "Use digits to set photos amount!\n(ex. 3)"
msg_min_hotel_photos_amount = (
    "Min number of photos to display is {min_photos}."
    "\n(ex. {min_photos})".format(min_photos=min_hotel_photos_amount)
)
msg_max_hotel_photos_amount = (
    "Max number of hotel photos to display is {max_photos}."
    "\n(ex. {max_photos})".format(max_photos=max_hotel_photos_amount)
)
state_data = {"commence_search": "initialized"}


def handle_hotel_photos_amount(
        chat_id: int, user_id: int, photos_amount: str,
) -> None:
    """Handle user input data for setting hotels photo amount.

    If hotels photo amount as per required format, then save the above data
    into bot state storage and send hotels search result.
    Other vice send  message  with corrective actions.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        photos_amount (str): hotel photos amount to display

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {photos_amount=}")
    if StateData.get_user_data_by_key(chat_id, user_id, "commence_search"):
        reply_msg = msg_searching_hotels
    else:
        photos_amount = get_int_number(photos_amount)
        error_msg = check_hotel_photos_amount(photos_amount)
        if not error_msg:
            state_data["hotel_photo_amount"] = photos_amount
            StateData.save_multiple_user_data(chat_id, user_id, state_data)
            handle_hotel_search(chat_id, user_id)
            return
        reply_msg = error_msg
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)


def check_hotel_photos_amount(photos_amount: Optional[int]) -> Optional[str]:
    """Check hotels photos amount.

    Return error message if photos_amount is not as per format digit
    [min_hotel_photos_amount, max_hotel_photos_amount].

    Args:
        photos_amount (int):  number of photos to display

    Returns:
        Optional[str]: error message

    """
    error_msg = None
    if not photos_amount and photos_amount != 0:
        error_msg = msg_use_digits
    elif photos_amount > max_hotel_photos_amount:
        error_msg = msg_max_hotel_photos_amount
    elif photos_amount < min_hotel_photos_amount:
        error_msg = msg_min_hotel_photos_amount
    bot_logger.debug(f"{photos_amount=}, {error_msg=}")
    return error_msg
