"""Module for launching Telegram Bot 'Global Hotel Search'"""

from sys import exit

from telebot.custom_filters import StateFilter

from loader import bot
import handlers
from utils.set_bot_commands import set_bot_commands
from keyboards.inline.calender.filters import add_calendar_filters


def load_telegram_bot() -> None:
    """Setting state filters, bot commands and launches telegram bot."""

    bot.add_custom_filter(StateFilter(bot))
    add_calendar_filters(bot)
    set_bot_commands(bot)
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    load_telegram_bot()
else:
    exit("Access is denied")
