"""Module for catching bot commands."""

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


@bot.message_handler(commands=[BEST_DEALS_COMMAND_DATA["command"]])
def best_deal_command(message: Message) -> None:
    """Catch unstated text message with bot command "best_deal".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_best_deal_command(message.chat.id, message.from_user.id)


@bot.message_handler(
    state="*", commands=[CANSEL_SEARCH_COMMAND_DATA["command"]],
)
def cansel_search_command(message: Message) -> None:
    """Catch any state text message with bot command "cancel_search".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_cancel_search_command(message.chat.id, message.from_user.id)


@bot.message_handler(commands=[HELP_COMMAND_DATA["command"]])
def help_command(message: Message) -> None:
    """Catch unstated text message with bot command "help".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_help_command(message.chat.id, message.from_user.id)


@bot.message_handler(commands=[HIGH_PRICE_COMMAND_DATA["command"]])
def high_price_command(message: Message) -> None:
    """Catch unstated text message with bot command "high_price".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_high_price_command(message.chat.id, message.from_user.id)


@bot.message_handler(commands=[HISTORY_COMMAND_DATA["command"]])
def history_command(message: Message) -> None:
    """Catch unstated text message with bot command "history".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_history_search_command(message.chat.id, message.from_user.id)


@bot.message_handler(commands=[LOW_PRICE_COMMAND_DATA["command"]])
def low_price_command(message: Message) -> None:
    """Catch unstated text message with bot command "low_price".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_low_price_command(message.chat.id, message.from_user.id)


@bot.message_handler(commands=[START_COMMAND_DATA["command"]])
def start_command(message: Message) -> None:
    """Catch unstated text message with bot command "start".

    Call command handler.

    Args:
        message (Message): user reply data

    """
    bot_logger.info(f"{message.chat.id=},{message.from_user.id=}")
    handle_start_command(
        message.chat.id, message.from_user.id, message.from_user.full_name,
    )
