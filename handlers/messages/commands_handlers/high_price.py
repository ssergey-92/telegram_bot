"""Module for handling high_price command."""

from .common import msg_type_city_name
from config_data.config import HIGH_PRICE_COMMAND_DATA
from database.crud_history_interface import HistoryCRUD
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger
from states.luxury_search import LuxurySearchStates

initialization_data = {
    "command":  HIGH_PRICE_COMMAND_DATA["shortcut"],
    "min_price": 1,
    "max_price": 1000000,
    "sort": "PRICE_LOW_TO_HIGH",
}
msg_selected_high_price = "Selected {command_shortcut}".format(
    command_shortcut=HIGH_PRICE_COMMAND_DATA["shortcut"]
)


def handle_high_price_command(chat_id: int, user_id: int) -> None:
    """Handle high_price command from user.

    Delete previous user state data, set new state, save data id db and bot
    state storage and send message for new state.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    bot.send_message(chat_id, msg_selected_high_price)
    StateData.delete_state(chat_id, user_id)
    bot.set_state(user_id, LuxurySearchStates.input_city, chat_id)
    history_id = HistoryCRUD.create_entry(
        user_id, HIGH_PRICE_COMMAND_DATA["shortcut"],
    )
    initialization_data["history_id"] = history_id
    StateData.save_multiple_user_data(chat_id, user_id, initialization_data)
    bot_logger.debug(f"{chat_id=}, {user_id=}, {msg_type_city_name=}")
    bot.send_message(
        chat_id, msg_type_city_name, reply_markup=cancel_reply_keyboard,
    )
