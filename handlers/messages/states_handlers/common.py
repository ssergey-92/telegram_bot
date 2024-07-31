"""Module with common functions for package."""

from calendar import month_abbr
from datetime import datetime, date, timedelta
from typing import Optional

from telebot.types import CallbackQuery

from keyboards.inline.calender.keyboards import (
    get_current_calendar_days_keyboard,
)
from loader import bot
from project_logging.bot_logger import bot_logger


def get_int_number(number: str) -> Optional[int]:
    """Strip and convert digit number from str to int format.

    Args:
        number (str): str number in digits.

    Returns:
        Optional[int]: int number.

    """
    bot_logger.debug(f"{number=}")
    try:
        number = number.strip("., ")
        int_number = int(number)
    except ValueError as exc:
        bot_logger.debug(f"{exc=}")
        int_number = None
    bot_logger.debug(f"{int_number=}")
    return int_number


def get_next_day_date(user_date: dict) -> str:
    """Increase user date by 1 day and convert to format(%d.%m.%Y).

    Args:
        user_date (dict): user date.

    Returns:
        str: date increased by 1 day

    """
    formatted_date = date(
        user_date["year"], user_date["month"], user_date["day"],
    )
    next_date = formatted_date + timedelta(days=1)
    bot_logger.debug(f"{user_date=}, {next_date=}")
    return next_date.strftime("%d.%m.%Y")


def convert_date_from_str_to_dict(user_date: str) -> dict:
    """Convert date from str ('30.07.2024') to dict format.

    Args:
        user_date (str): user date.

    Returns
    dict: date in dict format.

    """
    user_date = user_date.split(".")
    user_date = {
        "day": int(user_date[0]),
        "month": int(user_date[1]),
        "year": int(user_date[2]),
    }
    return user_date


def check_date_format(user_date: str) -> Optional[str]:
    """Check that date is existed and have format(%d.%m.%Y).

    Return exception message if date is not matching with parameters.

    Args:
        user_date (str): user date.

    Returns:
        Optional[str]: exception message | None

    """
    try:
        user_date = user_date.strip()
        datetime.strptime(user_date, "%d.%m.%Y")
        bot_logger.debug(f"{user_date=} is valid")
        return None
    except ValueError as exc:
        exception_message = str(exc).lstrip("ValueError").capitalize()
        bot_logger.debug(f"{user_date=}, {exception_message=} ")
        return exception_message


def extract_date_from_callback(call: CallbackQuery) -> Optional[dict]:
    """Extract date from callback calendar inline keyboard.

    Args:
        call (CallbackQuery): Callback button.

    Returns:
        Optional[dict]: date

    """
    try:
        json_data = call.json
        keyboard_date_data = (
            json_data["message"]["reply_markup"]["inline_keyboard"][0][0]["text"]
        )
        user_month, user_year = keyboard_date_data.split()
        user_day = call.data.rstrip("🔘")
        converted_month = list(month_abbr).index(user_month)
        user_date = {
            "day": int(user_day),
            "month": int(converted_month),
            "year": int(user_year),
        }
        bot_logger.debug(f"{keyboard_date_data=}, {user_date=}")
        return user_date
    except (KeyError, ValueError, TypeError) as exc:
        bot_logger.debug(f"{call.data=}, {exc=}")
        return None


def send_calendar_callback_error_msg(chat_id: int) -> None:
    """Send calendar error message with calendar reply keyboard

    Args:
        chat_id (int): user chat identifier

    """
    reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
    bot_logger.debug(f"{chat_id=}, {reply_text=}")
    reply_markup = get_current_calendar_days_keyboard()
    bot.send_message(chat_id, reply_text, reply_markup=reply_markup)


def send_invalid_format_date_msg(exception_msg: str, chat_id: int) -> None:
    """Send date format error message with calendar reply keyboard

    Args:
        exception_msg (str): exception message
        chat_id (int): user chat identifier

    """
    reply_text = "{exception_msg}.\nKindly use calendar.".format(
        exception_msg=exception_msg,
    )
    if reply_text.find("does not match format") > -1:
        reply_text = (
            "Use format to enter date dd.mm.yyyy\n(ex. {current_date})".format(
                current_date=date.today().strftime("%d.%m.%Y"),
            )
        )
    bot_logger.debug(f"{chat_id=}, {reply_text=}")
    reply_markup = get_current_calendar_days_keyboard()
    bot.send_message(chat_id, reply_text, reply_markup=reply_markup)
