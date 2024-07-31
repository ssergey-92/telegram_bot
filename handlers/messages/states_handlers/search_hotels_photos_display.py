"""Module for handling hotels_photos_display.

Contains common handling functions to handle hotel photos to display or not
from message for CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from telebot.handler_backends import State

from .search_hotel_photos_amount import (
    max_hotel_photos_amount,
    msg_searching_hotels,
)
from .search_result import handle_hotel_search
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_photos_amount_display = (
    "How many photos to display (max {max_hotel_photos})?".format(
        max_hotel_photos=max_hotel_photos_amount,
    )
)
msg_type_yes_no = "Type 'yes' or 'no'.\n(ex. yes)"
expected_user_response = ["yes", "no"]
state_data_without_photos = {
    "display_hotel_photos": False,
    "hotel_photo_amount": 0,
    "commence_search": "initialized",
}
state_data_with_photos = {"display_hotel_photos": True}


def handle_hotel_photos_display(
        chat_id: int, user_id: int, show_photo: str, next_state: State,
) -> None:
    """Handle user input data for showing hotels photos.

    If show_photo is "yes", then save data into bot state storage, set next
    state(next_state) and send message for next state.
    Elif show_photo is "no", save the above data into bot state storage and
    call handling func to make final response for hotel search request.
    Else send message  with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        show_photo (str): hotel photos to display.
        next_state (State): next search state.

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {show_photo=}, {next_state=}")
    if StateData.get_user_data_by_key(chat_id, user_id, "commence_search"):
        reply_msg = msg_searching_hotels
    else:
        show_photo = show_photo.strip().lower()
        if show_photo == "no":
            StateData.save_multiple_user_data(
                chat_id, user_id, state_data_without_photos,
            )
            handle_hotel_search(chat_id, user_id)
            return
        elif show_photo == "yes":
            reply_msg = msg_photos_amount_display
            StateData.save_multiple_user_data(
                chat_id, user_id, state_data_with_photos,
            )
            bot.set_state(user_id, next_state, chat_id)
        else:
            reply_msg = msg_type_yes_no
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
