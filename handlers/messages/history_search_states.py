"""Module for catching and handling each state in HistoryStates"""

from telebot.types import Message

from .states_handlers.history_records_number import handle_records_number
from loader import bot
from project_logging.bot_logger import bot_logger
from states.history import HistoryStates


@bot.message_handler(state=HistoryStates.records_number)
def records_number_state(message: Message) -> None:
    """Get state: HistoryStates.records_number and call handling function.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(
        f"{message.chat.id=}, {message.from_user.id=}, {message.text=}"
    )
    handle_records_number(
        message.chat.id, message.from_user.id, message.text,
    )
