from calendar import month_abbr
from typing import Union, Optional
from datetime import datetime

from telebot.types import CallbackQuery


def extract_date(call: CallbackQuery) -> Union[dict, bool]:
    try:
        json_data = call.json
        user_month, user_year = \
            json_data['message']['reply_markup']['inline_keyboard'][0][0]['text'].split()
        user_day = call.data.rstrip('🔘')
        converted_month = list(month_abbr).index(user_month)
        user_date = {"day": int(user_day),
                     "month": int(converted_month),
                     "year": int(user_year)}
    except ValueError as exc:
        return False
    else:
        return user_date


def valid_check_in_date(check_in_date: dict) -> bool:
    converted_date = datetime(check_in_date["year"], check_in_date["month"],
                              check_in_date["day"], 23, 59, 59)
    current_date = datetime.now()
    if converted_date >= current_date:
        return True
    else:
        return False


def valid_check_out_date(check_in_date: dict, check_out_date: dict) -> bool:
    converted_check_in_date = datetime(check_in_date["year"],
                                       check_in_date["month"], check_in_date["day"])
    converted_check_out_date = datetime(check_out_date["year"],
                                        check_out_date["month"], check_out_date["day"])
    if converted_check_out_date > converted_check_in_date:
        return True
    else:
        return False


def check_date_format(user_date: str) -> Optional[str]:
    user_date = user_date.strip()
    try:
        data = datetime.strptime(user_date, "%d.%m.%Y")
    except ValueError as exc:
        exception_message = str(exc).lstrip('ValueError').capitalize()
        return exception_message
    else:
        return None


def convert_str_date_to_dict(user_date: str) -> dict:
    user_date = user_date.split('.')
    user_date = {"day": int(user_date[0]),
                 "month": int(user_date[1]),
                 "year": int(user_date[2])}
    return user_date
