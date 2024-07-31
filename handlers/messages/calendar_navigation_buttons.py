from telebot.types import CallbackQuery

from keyboards.inline.calender.filters import calendar_factory, calendar_zoom
from keyboards.inline.calender.keyboards import (
    generate_calendar_days,
    generate_calendar_months,
)
from loader import bot


@bot.callback_query_handler(
    func=None, calendar_config=calendar_factory.filter(),
)
def calendar_action_handler(call: CallbackQuery) -> None:
    """Catch callback query with calendar_config from calendar

    Create new calendar inline keyboard for selected month based on callback
    data.
    (Pressed calendar buttons: 'Previous month', 'Next month' or 'Zoom in')

    Args:
        call (CallbackQuery): user reply data

    """

    callback_data: dict = calendar_factory.parse(callback_data=call.data)
    year, month = int(callback_data["year"]), int(callback_data["month"])

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=generate_calendar_days(year=year, month=month),
    )


@bot.callback_query_handler(
    func=None, calendar_zoom_config=calendar_zoom.filter(),
)
def calendar_zoom_out_handler(call: CallbackQuery) -> None:
    """Catch callback query with calendar_config from calendar

    Create new calendar inline keyboard for year with months based on callback
    data.
    (Pressed calendar buttons: "Zoom out", "previous year" or "next year").

    Args:
        call (CallbackQuery): user reply data

    """
    callback_data: dict = calendar_zoom.parse(callback_data=call.data)
    year = int(callback_data.get("year"))
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=generate_calendar_months(year=year),
    )
