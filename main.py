from sys import exit
from loguru import logger

from loader import bot
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_bot_commands

from keyboards.inline_keyboard.calender.filters import (
    CalendarCallbackFilter, CalendarZoomCallbackFilter)
import handlers
import database


@logger.catch()
def load_telegram_bot() -> None:
    bot.add_custom_filter(StateFilter(bot))
    bot.add_custom_filter(CalendarCallbackFilter())
    bot.add_custom_filter(CalendarZoomCallbackFilter())
    set_bot_commands(bot)
    bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    load_telegram_bot()
else:
    exit('Access is denied')
