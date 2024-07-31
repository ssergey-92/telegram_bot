"""Module for catching bot commands shortcuts from any state message."""

from telebot.types import Message

from .commands_handlers.best_deal import handle_best_deal_command
from .commands_handlers.cancel_search import handle_cancel_search_command
from .commands_handlers.help import handle_help_command
from .commands_handlers.high_price import handle_high_price_command
from .commands_handlers.history import handle_history_search_command
from .commands_handlers.low_price import handle_low_price_command
from .commands_handlers.start import handle_start_command
from config_data.config import (
    START_COMMAND_DATA,
    CANSEL_SEARCH_COMMAND_DATA,
    HELP_COMMAND_DATA,
    LOW_PRICE_COMMAND_DATA,
    HIGH_PRICE_COMMAND_DATA,
    BEST_DEALS_COMMAND_DATA,
    HISTORY_COMMAND_DATA,
)
from loader import bot
from project_logging.bot_logger import bot_logger


@bot.message_handler(regexp=BEST_DEALS_COMMAND_DATA["shortcut"])
def best_deal_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "Custom Hotel Search".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_best_deal_command(message.chat.id, message.from_user.id)


@bot.message_handler(state="*", regexp=CANSEL_SEARCH_COMMAND_DATA["shortcut"])
def cansel_search_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "Cancel Current Search".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_cancel_search_command(message.chat.id, message.from_user.id)


@bot.message_handler(regexp=HELP_COMMAND_DATA["shortcut"])
def help_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "Help".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_help_command(message.chat.id, message.from_user.id)


@bot.message_handler(regexp=HIGH_PRICE_COMMAND_DATA["shortcut"])
def high_price_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "Top Luxury Hotels".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_high_price_command(message.chat.id, message.from_user.id)


@bot.message_handler(regexp=HISTORY_COMMAND_DATA["shortcut"])
def history_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "History search".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_history_search_command(message.chat.id, message.from_user.id)


@bot.message_handler(regexp=LOW_PRICE_COMMAND_DATA["shortcut"])
def low_price_command_shortcut(message: Message) -> None:
    """Catch message contains command shortcut "Top Budget Hotels".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_low_price_command(message.chat.id, message.from_user.id)


@bot.message_handler(regexp=START_COMMAND_DATA["shortcut"])
def start_command(message: Message) -> None:
    """Catch message contains command shortcut "Start Bot".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_start_command(
        message.chat.id, message.from_user.id, message.from_user.full_name,
    )
