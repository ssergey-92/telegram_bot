"""Module for handling start command."""

from keyboards.inline.start import start_inline_keyboard
from loader import bot
from handlers.messages.utils.state_data import StateData
from project_logging.bot_logger import bot_logger

blank_msg_start = (
        "Welcome, {name}!\nI'm Hotel Dataprovider Bot from Too "
        "Easy Travel Agency.\nI can help you to find a suitable hotel."
)


def handle_start_command(chat_id: int, user_id: int, user_name: str) -> None:
    """Handle start command from user.

    Delete user state data if it is existed and send start message.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        user_name (str): username

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    StateData.delete_state(chat_id, user_id)
    msg_start = blank_msg_start.format(name=user_name)
    bot_logger.debug(f"{chat_id=}, {user_id=}, {msg_start=}")
    bot.send_message(chat_id, msg_start, reply_markup=start_inline_keyboard)
