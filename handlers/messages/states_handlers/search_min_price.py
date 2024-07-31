"""Module for handling min_price state for CustomSearchStates scenarios."""

from telebot.handler_backends import State

from .common import get_int_number
from .search_max_price import max_allowed_max_price
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_set_max_price = (
    "Type maximum hotel price per day in USD:\n(ex. max: {max_price})".format(
        max_price=max_allowed_max_price,
    )
)
msg_use_digits = "Use digits only to set min price!\n(ex. 50)"
min_allowed_min_price = 1
msg_min_allowed_min_price = (
    "Minimum price per day is {min_price} USD!\n(ex. {min_price}".format(
        min_price=min_allowed_min_price,
    )
)
max_allowed_min_price = 100000
msg_max_allowed_min_price = (
    "Maximum price per day is {max_price} USD!\n(ex. {max_price})".format(
        max_price=max_allowed_min_price,
    )
)


def handle_min_price(
        chat_id: int, user_id: int, min_price: str, next_state: State,
) -> None:
    """Handle user input data for setting minimum hotel price per day.

    If user input minimum hotel price per day as per format digit
    [min_allowed_min_price, msg_min_allowed_price], then save data into bot
    state storage, set next state and send message for next state.
    Other vice send message with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        min_price (str): min hotel price per day
        next_state (State): next state

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}, {min_price=}, {next_state=}")
    min_price = get_int_number(min_price)
    if not min_price and min_price != 0:
        reply_msg = msg_use_digits
    elif min_price < min_allowed_min_price:
        reply_msg = msg_min_allowed_min_price
    elif min_price > max_allowed_min_price:
        reply_msg = msg_max_allowed_min_price
    else:
        bot.set_state(user_id, next_state, chat_id)
        StateData.save_single_user_data(
            chat_id, user_id, "min_price", min_price,
        )
        reply_msg = msg_set_max_price
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=cancel_reply_keyboard)
