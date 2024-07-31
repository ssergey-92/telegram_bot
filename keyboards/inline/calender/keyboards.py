"""Module for creating calendars inline keyboards."""

import calendar
from datetime import date, timedelta

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from .filters import calendar_factory, calendar_zoom

months = [(i, calendar.month_name[i]) for i in range(1, 13)]
week_days = [calendar.day_abbr[i] for i in range(7)]


def add_month_days_to_calendar_keyboard(
        keyboard: InlineKeyboardMarkup, year: int, month: int,
) -> InlineKeyboardMarkup:
    """Add days of the month to calendar inline keyboard.

    Args:
        keyboard (InlineKeyboardMarkup): calendar inline keyboard
        year (int): year
        month (int): month

    Returns:
        InlineKeyboardMarkup: calendar inline keyboard

    """
    today = date.today()
    for week in calendar.Calendar().monthdayscalendar(year=year, month=month):
        week_buttons = []
        for day in week:
            day_name = " "
            if (
                day == today.day
                and today.year == year
                and today.month == month
            ):
                day_name = str(day) + "🔘"
            elif day != 0:
                day_name = str(day)
            week_buttons.append(
                InlineKeyboardButton(text=day_name, callback_data=day_name)
            )
        keyboard.add(*week_buttons)
    return keyboard


def add_navigation_buttons_to_calendar_keyboard(
        keyboard: InlineKeyboardMarkup, year: int, month: int,
) -> InlineKeyboardMarkup:
    """Add buttons navigation buttons to calendar inline keyboard.

    Navigation buttons :zoom out, next and previous month.

    Args:
        keyboard (InlineKeyboardMarkup): calendar inline keyboard
        year (int): year
        month (int): month

    Returns:
        InlineKeyboardMarkup: calendar inline keyboard

    """
    previous_month = date(year=year, month=month, day=1) - timedelta(days=1)
    next_month = date(year=year, month=month, day=1) + timedelta(days=31)
    keyboard.add(
        InlineKeyboardButton(
            text="Previous month",
            callback_data=calendar_factory.new(
                year=previous_month.year, month=previous_month.month
            ),
        ),
        InlineKeyboardButton(
            text="Zoom out", callback_data=calendar_zoom.new(year=year)
        ),
        InlineKeyboardButton(
            text="Next month",
            callback_data=calendar_factory.new(
                year=next_month.year, month=next_month.month
            ),
        ),
    )
    return keyboard


def generate_calendar_days(year: int, month: int) -> InlineKeyboardMarkup:
    """Create primary screen of calendar inline keyboard with days for month.

     Part 1 of 2 for calendar inline keyboard.

    Args:
        year (int): year
        month (int): month

    Returns:
        InlineKeyboardMarkup: first screen of calendar with days for month

    """
    keyboard = InlineKeyboardMarkup(row_width=7)

    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=month, day=1).strftime("%b %Y"),
            callback_data="EMTPY_FIELD1",
        )
    )
    keyboard.add(
        *[
            InlineKeyboardButton(text=day, callback_data="EMTPY_FIELD2")
            for day in week_days
        ]
    )
    keyboard = add_month_days_to_calendar_keyboard(keyboard, year, month)
    keyboard = add_navigation_buttons_to_calendar_keyboard(
        keyboard, year, month,
    )
    return keyboard


def generate_calendar_months(year: int) -> InlineKeyboardMarkup:
    """Create second screen of calendar inline keyboard with months for year.

    Part 2 of 2 for calendar inline keyboard.

    :param year: year
    :type year: int

    :return: second calendar screen with months for year
    :rtype:  InlineKeyboardMarkup

    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=1, day=1).strftime("Year %Y"),
            callback_data="EMTPY_FIELD4",
        )
    )
    keyboard.add(
        *[
            InlineKeyboardButton(
                text=month,
                callback_data=calendar_factory.new(
                    year=year, month=month_number
                ),
            ) for month_number, month in months
        ]
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Previous year",
            callback_data=calendar_zoom.new(year=year - 1),
        ),
        InlineKeyboardButton(
            text="Next year", callback_data=calendar_zoom.new(year=year + 1)
        ),
    )
    return keyboard


def get_current_calendar_days_keyboard() -> InlineKeyboardMarkup:
    """Create calendar inline keyboard with days for current month.

    :return: calendar with days for current month
    :rtype: InlineKeyboardMarkup

    """
    now = date.today()
    calendar_days_keyboard = generate_calendar_days(now.year, now.month)
    return calendar_days_keyboard


def get_current_calendar_months_keyboard() -> InlineKeyboardMarkup:
    """Create calendar inline keyboard with months for current year.

    :return: calendar with months for current year
    :rtype: InlineKeyboardMarkup

    """
    now = date.today()
    calendar_months_keyboard = generate_calendar_months(now.year)
    return calendar_months_keyboard
