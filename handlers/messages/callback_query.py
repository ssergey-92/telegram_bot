"""Module for catching callback query data with func=True and without state.

Handling call.data which contains dot commands.
"""

from telebot.types import CallbackQuery

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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery) -> None:
    """Catch unstated incoming callback query from inline keyboard.

    Call appropriate handling function according to bot commands.

    Args:
        call (CallbackQuery): user reply data from inline keyboard

    """
    bot_logger.info(
        f"{call.data=}, {call.message.chat.id=}, {call.from_user.id=}"
    )
    if call.data == START_COMMAND_DATA["command"]:
        handle_start_command(
            call.message.chat.id, call.from_user.id, call.from_user.full_name,
        )
    elif call.data == CANSEL_SEARCH_COMMAND_DATA["command"]:
        handle_cancel_search_command(call.message.chat.id, call.from_user.id)
    elif call.data == HELP_COMMAND_DATA["command"]:
        handle_help_command(call.message.chat.id, call.from_user.id)
    elif call.data == LOW_PRICE_COMMAND_DATA["command"]:
        handle_low_price_command(call.message.chat.id, call.from_user.id)
    elif call.data == HIGH_PRICE_COMMAND_DATA["command"]:
        handle_high_price_command(call.message.chat.id, call.from_user.id)
    elif call.data == BEST_DEALS_COMMAND_DATA["command"]:
        handle_best_deal_command(call.message.chat.id, call.from_user.id)
    elif call.data == HISTORY_COMMAND_DATA["command"]:
        handle_history_search_command(call.message.chat.id, call.from_user.id)
