"""Module for setting telegram bot commands"""

from telebot import TeleBot
from telebot.types import BotCommand


from config_data.config import BOT_COMMANDS


def set_bot_commands(bot: TeleBot) -> None:
    """Set telegram bot commands.

    Args:
        bot (bot): Telegram bot from pyTelegramBotApi

    """
    bot_commands_list = []
    for commands in BOT_COMMANDS.values():
        for i_command in commands:
            bot_commands_list.append(
                BotCommand(i_command["command"], i_command["shortcut"])
            )
    bot.set_my_commands(bot_commands_list)
