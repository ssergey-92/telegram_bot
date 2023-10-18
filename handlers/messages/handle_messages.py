from calendar import month_abbr
from datetime import datetime
from abc import ABC
from datetime import date
from typing import Optional, Union
from telebot.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                           CallbackQuery, Message)

from loader import bot
from database.history_model import History, db
from database.CRUD_interface import CrudDb
from states.BudgetSearch import BudgetSearchStates
from config_data.config import BOT_COMMANDS
from handlers.sites_API.rapidapi_hotels import HotelsApi

from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from keyboards.inline_keyboard.search_cities import (
    create_search_city_inline_keyboard)
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard
from .utils.state_data import StateData


class HandleMsg(ABC):

    @staticmethod
    def initialize_command(chat_id: int, user_id: int, cmd_shortcut: str, sort: str,
                           min_price: int, max_price: int, ) -> None:
        initialization_data = {"command": cmd_shortcut,
                               "min_price": min_price,
                               "max_price": max_price,
                               "sort": sort}
        StateData.delete_state(chat_id, user_id)
        bot.set_state(user_id, BudgetSearchStates.input_city, chat_id)
        StateData.save_multiple_data(chat_id, user_id, initialization_data)
        CrudDb.create_entries(db, History, user_id, cmd_shortcut)
        bot.send_message(chat_id, 'Type city name:',
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def input_city(chat_id: int, user_id: int, input_city_text: str, cmd_shortcut: str) \
            -> None:
        input_city = input_city_text.strip(',. ').replace(',', '').lower()
        reply_markup = cancel_reply_keyboard
        if HandleMsg._city_text_check(input_city):
            cities_data = HotelsApi.check_city(user_id, input_city_text, cmd_shortcut)
            if cities_data:
                reply_text = "You mean:"
                bot.set_state(user_id, BudgetSearchStates.confirm_city, chat_id)
                city_info = {"Input city": input_city_text,
                             "searched_city_result": cities_data}
                StateData.save_multiple_data(chat_id, user_id, city_info)
                reply_markup = create_search_city_inline_keyboard(cities_data)
            else:
                reply_text = ("Sorry, there is no city '{input_city}' in our database.\n"
                              "Try to enter proper city name or use another place.".format(
                    input_city=input_city_text)
                )
        else:
            reply_text = "Enter a city name using ENGLISH letters only!\n(ex. Miami)"
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def _city_text_check(input_city_text: str) -> bool:
        a_latter = ord('a')
        z_latter = ord('z')
        for i_word in input_city_text.split(' '):
            for i_letter in i_word:
                if not a_latter <= ord(i_letter) <= z_latter:
                    return False
        return True

    @staticmethod
    def confirm_city(chat_id: int, user_id: int,
                     confirm_city_id: Optional[str] = None) -> None:
        cities_data = StateData.retrieve_data_by_key(chat_id, user_id,
                                                     "searched_city_result")
        if confirm_city_id == "Type another city":
            reply_text = 'Type city name:'
            reply_markup = cancel_reply_keyboard
        elif confirm_city_id:
            reply_text = "Select check in date:"
            confirmed_city = cities_data[int(confirm_city_id)]
            bot.set_state(user_id, BudgetSearchStates.check_in_date, chat_id)
            StateData.save_multiple_data(chat_id, user_id, confirmed_city)
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
        else:
            reply_text = "Kindly select one of the below options!"
            reply_markup = create_search_city_inline_keyboard(cities_data)
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def check_in(check_in_info: Union[CallbackQuery, Message],
                 info_type: str) -> None:

        reply_text, check_in_date, user_id, chat_id = \
            HandleMsg._get_date_info_from_user_reply(info_type, check_in_info)
        if check_in_date and HandleMsg._valid_check_in_date(check_in_date):
            reply_text = "Select check out date:"
            bot.set_state(user_id, BudgetSearchStates.check_out_date, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "checkInDate", check_in_date)
    @staticmethod
    def _get_date_info_from_user_reply(info_type: str,
                                       check_in_info: Union[CallbackQuery, Message]) \
            -> tuple[Optional[str], Optional[dict], int, int]:
        reply_text = ""
        check_in_date = ""

        if check_in_info == "Message":
            exception_message = \
                HandleMsg._check_date_format(check_in_info.text)
            if exception_message:
                reply_text = "{exception_message}\n Use calendar!".format(
                    exception_message=exception_message)
            else:
                check_in_date = \
                    HandleMsg._convert_str_date_to_dict(check_in_info.text)
        else:
            check_in_date = \
                HandleMsg._extract_date_from_callback(check_in_info)
            if not check_in_date:
                reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
        return reply_text, check_in_date,

    @staticmethod
    def _extract_date_from_callback(call: CallbackQuery) -> Union[dict, bool]:
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

    @staticmethod
    def _check_date_format(user_date: str) -> Optional[str]:
        user_date = user_date.strip()
        try:
            data = datetime.strptime(user_date, "%d.%m.%Y")
        except ValueError as exc:
            exception_message = str(exc).lstrip('ValueError').capitalize()
            return exception_message
        else:
            return None

    @staticmethod
    def _valid_check_in_date(check_in_date: dict) -> bool:
        converted_date = date(check_in_date["year"], check_in_date["month"],
                              check_in_date["day"])
        current_date = date.today()
        if converted_date >= current_date:
            return True
        else:
            return False

    @staticmethod
    def _valid_check_out_date(check_in_date: dict, check_out_date: dict) -> bool:
        converted_check_in_date = datetime(check_in_date["year"],
                                           check_in_date["month"], check_in_date["day"])
        converted_check_out_date = datetime(check_out_date["year"],
                                            check_out_date["month"], check_out_date["day"])
        if converted_check_out_date > converted_check_in_date:
            return True
        else:
            return False

    @staticmethod
    def _convert_str_date_to_dict(user_date: str) -> dict:
        user_date = user_date.split('.')
        user_date = {"day": int(user_date[0]),
                     "month": int(user_date[1]),
                     "year": int(user_date[2])}
        return user_date
