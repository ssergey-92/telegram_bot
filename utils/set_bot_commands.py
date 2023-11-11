from telebot.types import BotCommand
from telebot import TeleBot

from config_data.config import BOT_COMMANDS


def set_bot_commands(bot: TeleBot) -> None:
    """
    Setting  commands for telegram bot.

    :param bot: Telegram bot from pyTelegramBotApi
    :type  bot: bot
    """

    bot.set_my_commands([BotCommand(
        command=command[0],
        description=command[1])
        for command in BOT_COMMANDS])
