"""Module for handling cancel_search command."""

from handlers.messages.utils.state_data import StateData
from keyboards.inline.start import start_inline_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_cancel_search = "Your search state was canceled."


def handle_cancel_search_command(chat_id: int, user_id) -> None:
    """Handle cansel search command from user.

    Delete user state data and send reply message.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    StateData.delete_state(chat_id, user_id)
    bot_logger.debug(f"{chat_id=}, {user_id=}, {msg_cancel_search=}")
    bot.send_message(
        chat_id, msg_cancel_search, reply_markup=start_inline_keyboard,
    )
