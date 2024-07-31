"""Module for handling help command."""

from config_data.config import BOT_COMMANDS
from handlers.messages.utils.state_data import StateData
from keyboards.reply.help import help_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

help_text_header: str = (
        "Kindly familiarize yourself with following commands:\n"
        "Command - Shortcut - Description\n"
)


def create_help_text() -> str:
    """Create help text which include bot commands, shortcuts and description.

    :return: help text
    :rtype: str

    """
    help_msg = help_text_header
    for commands in BOT_COMMANDS.values():
        for i_command in commands:
            command_details = (
                "/{command} - {shortcut} - {description}\n".format(
                    command=i_command["command"],
                    shortcut=i_command["shortcut"],
                    description=i_command["description"],
                )
            )
            help_msg += command_details
    bot_logger.debug(f"{help_msg=}")
    return help_msg


msg_help = create_help_text()


def handle_help_command(chat_id: int, user_id: int) -> None:
    """Handle help command from user.

    Delete user state data and send reply message.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    StateData.delete_state(chat_id, user_id)
    bot_logger.debug(f"{chat_id=}, {user_id=}, {msg_help=}")
    bot.send_message(chat_id, msg_help, reply_markup=help_reply_keyboard)
