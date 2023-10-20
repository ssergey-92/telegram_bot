from calendar import month_abbr
from datetime import datetime, date
from abc import ABC
from typing import Optional, Union

from telebot.types import (CallbackQuery, Message, InputMediaPhoto,
                           InlineKeyboardMarkup)
from telebot.handler_backends import StatesGroup
from loader import bot
from database.history_model import History, db
from database.CRUD_interface import CrudDb
from handlers.sites_API.rapidapi_hotels import HotelsApi
from .utils.state_data import StateData
from config_data.config import BOT_COMMANDS
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days)
from keyboards.inline_keyboard.search_cities import (
    create_search_city_inline_keyboard)
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard


class HandleMsg(ABC):

    @staticmethod
    def initialize_command(chat_id: int, user_id: int, cmd_shortcut: str, sort: str,
                           min_price: int, max_price: int, new_state: StatesGroup) \
            -> None:
        initialization_data = {"command": cmd_shortcut,
                               "min_price": min_price,
                               "max_price": max_price,
                               "sort": sort}
        StateData.delete_state(chat_id, user_id)
        bot.set_state(user_id, new_state, chat_id)
        StateData.save_multiple_data(chat_id, user_id, initialization_data)
        CrudDb.create_entries(db, History, user_id, cmd_shortcut)
        bot.send_message(chat_id, 'Type city name:',
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def input_city(chat_id: int, user_id: int, input_city_text: str,
                   cmd_shortcut: str, new_state: StatesGroup) -> None:
        input_city = input_city_text.strip(',. ').replace(',', '').lower()
        reply_markup = cancel_reply_keyboard
        if HandleMsg._check_eng_language(input_city):
            cities_data = HotelsApi.check_city(user_id, input_city_text, cmd_shortcut)
            if cities_data:
                reply_text = "You mean:"
                bot.set_state(user_id, new_state, chat_id)
                city_info = {"Input city": input_city_text,
                             "searched_city_result": cities_data}
                StateData.save_multiple_data(chat_id, user_id, city_info)
                reply_markup = create_search_city_inline_keyboard(cities_data)
            else:
                reply_text = ("Sorry, there is no city '{input_city}' in our database."
                              "\nTry to enter proper city name or use another "
                              "place").format(
                    input_city=input_city_text)
        else:
            reply_text = "Enter a city name using ENGLISH letters only!\n(ex. Miami)"
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def confirm_city(chat_id: int, user_id: int, new_state: StatesGroup,
                     previous_state: StatesGroup, reply_text: str = None,
                     city_id: Optional[str] = None,
                     reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
        cities_data = StateData.retrieve_data_by_key(chat_id, user_id,
                                                     "searched_city_result")
        if city_id == "Type another city":
            reply_text = 'Type city name:'
            reply_markup = cancel_reply_keyboard
            bot.set_state(user_id, previous_state, chat_id)
        elif city_id:
            confirmed_city = cities_data[int(city_id)]
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_multiple_data(chat_id, user_id, confirmed_city)
        else:
            reply_text = "Kindly select one of the below options!"
            reply_markup = create_search_city_inline_keyboard(cities_data)
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def set_min_price(chat_id: int, user_id: int, min_price: str,
                      new_state: StatesGroup) -> None:
        min_price = min_price.strip('., ')
        if not min_price.isdigit():
            reply_text = "Use digits only to set min price!\n(ex. 50)"
        elif int(min_price) == 0:
            reply_text = "Minimum price per day is 1 USD!\n(ex. 1)"
        else:
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "min_price", int(min_price))
            reply_text = "Type maximum hotel price in USD per day:\n"
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def set_max_price(chat_id: int, user_id: int, max_price: str,
                      new_state: StatesGroup) -> None:
        max_price = max_price.strip('., ')
        min_price = StateData.retrieve_data_by_key(chat_id, user_id, "min_price")
        if not max_price.isdigit():
            reply_text = "Use digits only to set min price!!\n(ex. 1000)"
        elif int(max_price) <= min_price:
            reply_text = ("Max price must be higher then min price: {min_price} "
                          "USD.".format(min_price=min_price))
        elif int(max_price) >= 1000000:
            reply_text = "Max hotel price per day is 1 000 000 USD!"
        else:
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "max_price", int(max_price))
            reply_text = ("Type minimum hotel distance in miles from city center.\n"
                          "*1 mile is 1.6 km")
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def set_min_distance(chat_id: int, user_id: int, min_distance: str,
                         new_state: StatesGroup) -> None:
        min_distance = min_distance.strip('., ')
        if not min_distance.isdigit():
            reply_text = ("Use digits only to set min distance from cite center!"
                          "\n(ex. 0)")
        elif int(min_distance) > 200:
            reply_text = "MAX min distance from cite center is 200!\n(ex. 200)"
        else:
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "min_distance", int(min_distance))
            reply_text = "Type maximum hotel distance in miles from city center."
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)


    @staticmethod
    def set_max_distance(chat_id: int, user_id: int, max_distance: str,
                         new_state: StatesGroup) -> None:
        max_distance = max_distance.strip('., ')
        min_distance = StateData.retrieve_data_by_key(chat_id, user_id,
                                                      "min_distance")
        reply_markup = cancel_reply_keyboard
        if not max_distance.isdigit():
            reply_text = ("Use digits only to set max distance from cite center!"
                          "\n(ex. 20)")
        elif int(max_distance) >= 300:
            reply_text = "MAX max distance from cite center is 300!\n(ex. 300)"
        elif int(max_distance) <= min_distance:
            reply_text = ("Max distance must be longer then min distance: "
                          "{min_distance}!".format(min_distance=min_distance))
        else:
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "max_distance", int(max_distance))
            reply_text = "Select check in date:"
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
        bot.send_message(chat_id, reply_text,
                         reply_markup=reply_markup)

    @staticmethod
    def check_calendar_callback(date_info: CallbackQuery) -> Optional[dict]:
        date_dict = HandleMsg._extract_date_from_callback(date_info)
        if not date_dict:
            reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
            bot.send_message(date_info.message.chat.id, reply_text,
                             reply_markup=reply_markup)
            return None
        return date_dict

    @staticmethod
    def check_calendar_message(date_info: Message) -> Optional[dict]:
        exception_message = HandleMsg._check_date_format(date_info.text)
        if exception_message:
            reply_text = "{exception_message}.\nKindly use calendar.".format(
                exception_message=exception_message)
            if reply_text.find("does not match format") > -1:
                reply_text = ("Use format to enter date dd.mm.yyyy\n"
                              "(ex. {present_day})".format(
                    present_day=date.today().strftime('%d.%m.%Y')))
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
            bot.send_message(date_info.chat.id, reply_text,
                             reply_markup=reply_markup)
            return None
        else:
            date_dict = HandleMsg._convert_str_date_to_dict(date_info.text)
            return date_dict

    @staticmethod
    def check_in(chat_id: int, user_id: int, check_in_date: dict,
                 new_state: StatesGroup) -> None:
        now = date.today()
        reply_markup = generate_calendar_days(year=now.year,
                                              month=now.month)
        if HandleMsg._valid_check_in_date(check_in_date):
            reply_text = "Select check out date:"
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "checkInDate", check_in_date)
        else:
            reply_text = "Select check in date starting {current_date}".format(
                current_date=date.today().strftime('%d %b %Y'))
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def check_out(chat_id: int, user_id: int, check_out_date: dict,
                  new_state: StatesGroup) -> None:
        check_in_date = StateData.retrieve_data_by_key(chat_id, user_id,
                                                       "checkInDate")
        if HandleMsg._valid_check_out_date(check_in_date, check_out_date):
            reply_text = "Type number of travellers (max 14): "
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "checkOutDate", check_out_date)
            reply_markup = cancel_reply_keyboard
        else:
            check_in_date = StateData.retrieve_data_by_key(chat_id,
                                                           user_id, 'checkInDate')
            reply_text = ("Select check out date after check in date"
                          " {day}.{month}.{year}").format(
                day=check_in_date["day"],
                month=check_in_date["month"],
                year=check_in_date["year"]
            )
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def set_travellers(chat_id: int, user_id: int, travellers_amount: str,
                       new_state: StatesGroup) -> None:
        travellers_amount = travellers_amount.strip()
        if not travellers_amount.isdigit():
            reply_text = "Use digits to set number of travellers!\n(ex. 2)"
        elif int(travellers_amount) >= 15:
            reply_text = "Max number of travellers is 14!\n(ex. 5)"
        elif int(travellers_amount) <= 0:
            reply_text = "Min number of travellers is 1!\n(ex. 1)"
        else:
            reply_text = "How many hotels to display (max 10)?"
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "adults", int(travellers_amount))
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def set_hotel_amount(chat_id: int, user_id: int, hotels_amount: str,
                         new_state: StatesGroup) -> None:
        reply_text = "Do you need photo of hotels?\nType 'yes' or 'no'."
        hotels_amount = hotels_amount.strip()
        if not hotels_amount.isdigit():
            reply_text = 'Use digits to set hotels amount!\n(ex. 3)'
        elif int(hotels_amount) >= 11:
            reply_text = "Max number of hotels to display is 10!\n(ex. 10)"
        elif int(hotels_amount) <= 0:
            reply_text = "Min number of hotels to display is 1!\n(ex. 1)"
        else:
            bot.set_state(user_id, new_state, chat_id)
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "hotels_amount", int(hotels_amount))
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def show_hotel_photo(chat_id: int, user_id: int, show_photo: str,
                         new_state: StatesGroup) -> None:
        if not StateData.retrieve_data_by_key(chat_id, user_id,
                                              "commence_search"):
            show_photo = show_photo.strip().lower()
            if not show_photo.isalpha():
                reply_text = "Use letters only!\n(ex. yes)"
            elif show_photo not in ['yes', 'no']:
                reply_text = "Type 'yes' or 'no'.\n(ex. yes)"
            elif show_photo == "no":
                last_step_data = {"display_hotel_photos": show_photo,
                                  "hotel_photo_amount": 0,
                                  "commence_search": 'initialized'}
                StateData.save_multiple_data(chat_id, user_id, last_step_data)
                HandleMsg._send_final_response(chat_id, user_id)
                return None
            else:
                reply_text = "How many photos to display (max 5)?"
                StateData.save_state_data_by_key(chat_id, user_id,
                                                 "display_hotel_photos", show_photo)
                bot.set_state(user_id, new_state, chat_id)
        else:
            reply_text = ("Kindly wait, searching for your suitable hotels.\n"
                          "*press cancel button if your want to break the search.")
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def set_photos_amount(chat_id: int, user_id: int, photo_amount: str) \
            -> None:
        if not StateData.retrieve_data_by_key(chat_id, user_id,
                                              "commence_search"):
            photo_amount = photo_amount.strip()
            if not photo_amount.isdigit():
                reply_text = "Use digits to set photos amount!\n(ex. 3)"
            elif int(photo_amount) > 5:
                reply_text = "Max number of photos to display is 5.\n(ex. 5)"
            elif int(photo_amount) <= 0:
                reply_text = "Min number of photos to display is 1.\n(ex. 1)"
            else:
                last_step_data = {"hotel_photo_amount": int(photo_amount),
                                  "commence_search": 'initialized'}
                StateData.save_multiple_data(chat_id, user_id, last_step_data)
                HandleMsg._send_final_response(chat_id, user_id)
                return None
        else:
            reply_text = ("Kindly wait, searching for your suitable hotels.\n"
                          "*press cancel button if your want to break the search.")
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def _send_final_response(chat_id: int, user_id: int) -> None:
        full_state_data = StateData.retrieve_full_data_by_id(chat_id, user_id)
        user_search_settings = HandleMsg._sort_user_search_settings(full_state_data)
        bot.send_message(chat_id, user_search_settings)
        CrudDb.update_last_user_entry(db, History, user_id, History.user_request,
                                      user_search_settings)
        bot.send_message(chat_id, "searching suitable hotels",
                         reply_markup=cancel_reply_keyboard)
        hotel_details = HotelsApi.find_hotels_in_city(chat_id, user_id)
        if StateData.retrieve_data_by_key(chat_id, user_id, "commence_search"):
            if hotel_details:
                if full_state_data["display_hotel_photos"] == "no":
                    reply_text = HandleMsg._create_final_message(hotel_details)
                    for i_text in reply_text:
                        bot.send_message(chat_id, i_text)
                else:
                    reply_text = HandleMsg._create_final_message_with_photo(hotel_details)
                    for i_text in reply_text:
                        bot.send_media_group(chat_id, i_text)
            else:
                reply_text = ("There is no available hotels as per your search settings.\n"
                              "Try again with another search configuration.")
                bot.send_message(chat_id, reply_text)
            CrudDb.update_last_user_entry(db, History, user_id, History.bot_response,
                                          reply_text)
            StateData.delete_state(chat_id, user_id)

    @staticmethod
    def _sort_user_search_settings(full_state_data: dict) -> str:
        request_details = ("Search settings:\n\n"
                           "Criteria: {command_shortcut}\n"
                           "City: {city}\n"
                           "Check in date: {ci_day}.{ci_month}.{ci_year}\n"
                           "Check out date: {co_day}.{co_month}.{co_year}").format(
            command_shortcut=full_state_data["command"],
            city=full_state_data['fullName'],
            ci_day=full_state_data["checkInDate"]["day"],
            ci_month=full_state_data["checkInDate"]["month"],
            ci_year=full_state_data["checkInDate"]["year"],
            co_day=full_state_data["checkOutDate"]["day"],
            co_month=full_state_data["checkOutDate"]["month"],
            co_year=full_state_data["checkOutDate"]["year"]
        )
        if full_state_data["command"] == BOT_COMMANDS[5][1]:  # best_deal shortcut(custom search)
            request_details = ("{request_details}\n"
                               "Price range: {min_price} - {max_price} per dayUSD\n"
                               "Distance range: {min_distance} - {max_distance} MILE"
                               "").format(
                request_details=request_details,
                min_price=full_state_data["min_price"],
                max_price=full_state_data["max_price"],
                min_distance=full_state_data["min_distance"],
                max_distance=full_state_data["max_distance"])
        request_details = ("{request_details}\n"
                           "Travellers: {travellers}\n"
                           "Hotels: {hotels_amount}\n"
                           "Hotel photos: {display_hotel_photos}").format(
            request_details=request_details,
            travellers=full_state_data["adults"],
            hotels_amount=full_state_data["hotels_amount"],
            display_hotel_photos=full_state_data["display_hotel_photos"].capitalize())
        if full_state_data["display_hotel_photos"] == "yes":
            request_details = ("{request_details}\n"
                               "Photos: {hotel_photo_amount}").format(
                request_details=request_details,
                hotel_photo_amount=full_state_data["hotel_photo_amount"]
            )
        return request_details

    @staticmethod
    def _create_final_message(hotel_details: list[dict]) -> list[str]:
        reply_text = list()
        for i_hotel in hotel_details:
            reply_text.append(HandleMsg._create_hotel_caption(i_hotel))
        return reply_text

    @staticmethod
    def _create_hotel_caption(i_hotel: dict) -> str:
        hotel_caption = ("Name: {hotel_name}\n"
                         "Price per day: {price_per_day}\n"
                         "Price per stay: {price_per_stay}\n"
                         "Rating: {rating}/5\n"
                         "Distance from city center: {distance}\n"
                         "Address: {hotel_address}\n"
                         "Website: {site_url}").format(
            hotel_name=i_hotel["name"],
            price_per_day=i_hotel["price_per_day"],
            price_per_stay=i_hotel["price_per_stay"],
            rating=i_hotel["hotel_rating"],
            distance=i_hotel["distance"],
            hotel_address=i_hotel["hotel_address"],
            site_url=i_hotel["site_url"]
        )

        return hotel_caption

    @staticmethod
    def _create_final_message_with_photo(hotel_details: list[dict]) \
            -> list[list[InputMediaPhoto]]:
        reply_text_with_photos = list()
        for i_hotel in hotel_details:
            hotel_caption = HandleMsg._create_hotel_caption(i_hotel)
            caption_count = 0
            temp_reply_text = list()
            for i_photo_url in i_hotel["photos_url"]:
                if caption_count == 0:
                    photo_media = [InputMediaPhoto(media=i_photo_url, caption=hotel_caption)]
                    caption_count += 1
                else:
                    photo_media = [InputMediaPhoto(media=i_photo_url)]
                temp_reply_text.extend(photo_media)
            reply_text_with_photos.append(temp_reply_text)
        return reply_text_with_photos

    @staticmethod
    def _check_eng_language(input_city_text: str) -> bool:
        a_latter = ord('a')
        z_latter = ord('z')
        for i_word in input_city_text.split(' '):
            for i_letter in i_word:
                if not a_latter <= ord(i_letter) <= z_latter:
                    return False
        return True

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
