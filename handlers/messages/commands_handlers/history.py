"""Module for handling 'history' command."""

from database.crud_history_interface import HistoryCRUD
from handlers.messages.states_handlers.history_records_number import (
    max_records,
    min_records,
    msg_no_records_found,
)
from handlers.messages.utils.state_data import StateData
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger
from states.history import HistoryStates

msg_select_records = (
    "Select number of records {min_records} to {max_records}:".format(
        min_records=min_records, max_records=max_records,
    )
)


def handle_history_search_command(chat_id: int, user_id: int) -> None:
    """Handle history command from user.

    Delete user state data set new history state if user's history record
    found.  Send new state  msg.

    Args:
        chat_id (int): chat identifier.
        user_id (int): user identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    StateData.delete_state(chat_id, user_id)
    if HistoryCRUD.get_latest_user_entries(user_id, 1):
        bot.set_state(user_id, HistoryStates.records_number, chat_id)
        reply_msg = msg_select_records
    else:
        reply_msg = msg_no_records_found
    bot_logger.debug(f"{chat_id=}, {user_id=}, {reply_msg=}")
    bot.send_message(
        chat_id, reply_msg, reply_markup=cancel_reply_keyboard,
    )
