import json
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
from handlers.messages.utils.state_data import StateData
from config_data.config import BOT_COMMANDS
from keyboards.inline_keyboard.start import start_inline_keyboard
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days)
from keyboards.inline_keyboard.search_cities import (
    create_search_city_inline_keyboard)
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard


class HandleSearchMsg(ABC):
    """
    Class HandleSearchMsg. Parent class(abc.ABC)
    Class for handling hotel search state messages.
    """

    @staticmethod
    def initialize_command(chat_id: int, user_id: int, cmd_shortcut: str, sort: str,
                           min_price: int, max_price: int, new_state: StatesGroup) \
            -> None:
        """
        Handling hotel search initialization command data from user.
        Deleting previous user state data if it exists, setting new search state,
        saving search details in History table of telegram_bot.db and
        bot state storage and sending reply message/asking city name for hotel
        search.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param cmd_shortcut: BOT_COMMANDS shortcut
        :type cmd_shortcut: str
        :param sort: sort parameter for hotel search post request
        :type sort: str
        :type min_price: minimum hotel price per day
        :param min_price: int
        :param max_price: maximum hotel price per day
        :type max_price: int
        :param new_state: next search state
        :type new_state: StatesGroup
        """

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
        """
        Handling user input data for search city name.
        If user input city name consists of english letters only,
        calling HotelsApi.check_city and sending sorted received response to user
        and saving the above data in bot state storage, setting
        new state(new_state) and sending reply message/asking to confirm city
        name for hotel search.
        Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param input_city_text: input city name by user
        :type input_city_text: str
        :param cmd_shortcut: BOT_COMMANDS shortcut
        :type cmd_shortcut: str
        :param new_state: next search state
        :type new_state: StatesGroup
        """

        input_city = input_city_text.strip(',. ').replace(',', '').lower()
        reply_markup = cancel_reply_keyboard
        if HandleSearchMsg._check_eng_language(input_city):
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
    def confirm_city(chat_id: int, user_id: int, next_state: StatesGroup,
                     previous_state: StatesGroup, reply_text: str = None,
                     city_id: Optional[str] = None,
                     reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
        """
        Handling user input data for confirming search city.
        If user input city name == "Type another city" setting previous state
        (previous_state) and sending message/asking to type city name .
        Elif user input city name consists of letters only, calling HotelsApi.check_city
        and sending sorted received response to user and saving the above data in
        bot state storage, setting new state(next_state) and sending
        message/asking info as per reply text.
        Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param next_state: next search state
        :type next_state: StatesGroup
        :param previous_state: previous search state
        :type previous_state: StatesGroup
        :param reply_text: user reply text
        :type reply_text: str
        :param city_id: city id
        :type city_id: Optional[str]
        :param reply_markup: inline keyboard markup
        :type reply_markup: Optional[InlineKeyboardMarkup]
        """

        cities_data = StateData.retrieve_data_by_key(chat_id, user_id,
                                                     "searched_city_result")
        if city_id == "Type another city":
            reply_text = 'Type city name:'
            reply_markup = cancel_reply_keyboard
            bot.set_state(user_id, previous_state, chat_id)
        elif city_id:
            confirmed_city = cities_data[int(city_id)]
            bot.set_state(user_id, next_state, chat_id)
            StateData.save_multiple_data(chat_id, user_id, confirmed_city)
        else:
            reply_text = "Kindly select one of the below options!"
            reply_markup = create_search_city_inline_keyboard(cities_data)
        bot.send_message(chat_id, reply_text, reply_markup=reply_markup)

    @staticmethod
    def set_min_price(chat_id: int, user_id: int, min_price: str,
                      new_state: StatesGroup) -> None:
        """
        Handling user input data for setting minimum hotel price per day.
        If user input minimum hotel price per day as per format(digit[1, 100000]),
        saving  the above data into bot state storage, setting new
        state(new_state) and sending message/asking to set maximum hotel
        price per day. Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param min_price: minimum hotel price per day
        :type min_price: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

        min_price = min_price.strip('., ')
        if not min_price.isdigit():
            reply_text = "Use digits only to set min price!\n(ex. 50)"
        elif int(min_price) == 0:
            reply_text = "Minimum price per day is 1 USD!\n(ex. 1)"
        elif int(min_price) >= 100000:
            reply_text = ("Max minimum price per day is 100 000 USD!"
                          "\n(ex. 10000)")
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
        """
        Handling user input data for setting maximum hotel price per day.
        If user input max hotel price per day as per format
        (digit[min_price, 100000]), saving  the above data into bot state storage,
        setting new state(new_state) and sending message/asking to set min
        hotel distance from city center.
        Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param max_price: minimum hotel price per day
        :type max_price: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
        """
        Handling user input data for setting minimum hotel distance from city
        center.
        If user input min hotel distance from city center as per format
        (digit[0, 199]),  saving the above data into bot state storage, setting new
        state(new_state) and sending message/asking to set max hotel distance
        from city center. Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param min_distance: minimum hotel distance from city center
        :type min_distance: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
        """
        Handling user input data for setting maximum hotel distance from city
        center.
        If user input max hotel distance from city center as per format
        (digit[min_distance, 299]), saving the above data into bot state storage,
        setting new state(new_state) and sending message/asking to set check
        in date. Other vice bot sends  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param max_distance: maximum hotel distance from city center
        :type max_distance: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
        """
        Sorting data from inline calendar button.
        If user pressed on button with date >= current date then return date.
        Other vice bot sends  message  with corrective action.

        :param date_info: date info from inline calendar button which  user pressed
        :type date_info: CallbackQuery
        :return: date
        :rtype: Optional[dict]
        """

        date_dict = HandleSearchMsg._extract_date_from_callback(date_info)
        if not date_dict:
            reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
            now = date.today()
            reply_markup = generate_calendar_days(year=now.year,
                                                  month=now.month)
            bot.send_message(date_info.message.chat.id, reply_text,
                             reply_markup=reply_markup)
        return date_dict

    @staticmethod
    def check_calendar_date(date_info: Message) -> Optional[dict]:
        """
        Checking date from user.
        If  user input date as per format(dd.mm.yyyy) and date >= current date
        then return date. Other vice bot sends  message  with corrective action.

        :param date_info: date info from inline calendar button which  user
        pressed
        :type date_info: CallbackQuery
        :return: date
        :rtype: Optional[dict]
        """

        exception_message = HandleSearchMsg._check_date_format(date_info.text)
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
        else:
            date_dict = HandleSearchMsg._convert_str_date_to_dict(
                date_info.text)
            return date_dict

    @staticmethod
    def check_in(chat_id: int, user_id: int, check_in_date: dict,
                 new_state: StatesGroup) -> None:
        """
        Handling user input data for setting check in date in hotel.
        If user input check in date is valid, saving the above data into bot state
        storage, setting new state(new_state) and sending message/asking to
        set check out date.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param check_in_date: check in date in hotel
        :type check_in_date: dict
        :param new_state: new search state
        :type new_state: StatesGroup
        """

        now = date.today()
        reply_markup = generate_calendar_days(year=now.year,
                                              month=now.month)
        if HandleSearchMsg._valid_check_in_date(check_in_date):
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
        """
        Handling user input data for setting check out date in hotel.
        If user input check out date is valid, saving the above data into bot state
        storage, setting new state(new_state) and sending message/asking to
        set number of travellers.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param check_out_date: check out date in hotel
        :type check_out_date: dict
        :param new_state: new search state
        :type new_state: StatesGroup
        """

        check_in_date = StateData.retrieve_data_by_key(chat_id, user_id,
                                                       "checkInDate")
        if HandleSearchMsg._valid_check_out_date(check_in_date, check_out_date):
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
        """
        Handling user input data for setting number of travellers.
        If user input number of travellers as per format(digit[1:15]), saving the
        above data into bot state storage, setting new state(new_state) and
        sending message/asking to set hotels amount to show.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param travellers_amount: number of travellers
        :type travellers_amount: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
        """
        Handling user input data for setting hotels amount to shows.
        If user input number of hotels amount to show(digit[1:10]), saving the
        above data into bot state storage, setting new state(new_state) and
        sending message/asking if required hotels photos to show.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param hotels_amount: number of travellers
        :type hotels_amount: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
        """
        Handling user input data for showing hotels photos.
        If user input is "yes", saving the above data into bot state storage,
        setting new state(new_state) and sending message/asking hom many
        hotels photos to display.
        Elif user input is "no", saving the above data into bot state storage and
        calling _create_final_response for making response on hotel search request.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param show_photo: show photo yes/no
        :type show_photo: str
        :param new_state: new search state
        :type new_state: StatesGroup
        """

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
                HandleSearchMsg._create_final_response(chat_id, user_id)
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
        """
        Handling user input data for setting hotels photo amount.
        If user input hotels photo amount (digit[1, 5], saving the above data into
        bot state storage and calling _create_final_response for making response
        on hotel search request.
        Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param photo_amount: number of photos to display
        :type photo_amount: str
        """

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
                HandleSearchMsg._create_final_response(chat_id, user_id)
                return None
        else:
            reply_text = ("Kindly wait, searching for your suitable hotels.\n"
                          "*press cancel button if your want to break the search.")
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def _create_final_response(chat_id: int, user_id: int) -> None:
        """
        Creating response with hotels details as per user hotel search
        request settings:
        -Sorting user hotel search request settings, then saving it in
        telegram_bot.db and sending to user.
        - Obtaining response info (HotelsApi.find_hotels_in_city())
        - Sending response to user (_send_final_massage()) if search state was
         not canceled by user.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        """

        full_state_data = StateData.retrieve_full_data_by_id(chat_id, user_id)
        user_search_settings = HandleSearchMsg._sort_user_search_settings(full_state_data)
        bot.send_message(chat_id, user_search_settings)
        CrudDb.update_last_user_entry(db, History, user_id, History.user_request,
                                      user_search_settings)
        bot.send_message(chat_id, "searching suitable hotels",
                         reply_markup=cancel_reply_keyboard)
        hotels_details = HotelsApi.find_hotels_in_city(chat_id, user_id)
        if StateData.retrieve_data_by_key(chat_id, user_id, "commence_search"):
            HandleSearchMsg._send_final_massage(chat_id, user_id, hotels_details,
                                                full_state_data["display_hotel_photos"])

    @staticmethod
    def _send_final_massage(chat_id: int, user_id: int, hotels_details: list[dict],
                            display_hotel_photos: str) -> None:
        """
        Sending hotels details to user if there is available hotels as per user
        request. Saving the above data  (_save_final_response_in_db)
        and deleting  current search state.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param hotels_details: hotels details
        :type hotels_details: list[dict]
        :param display_hotel_photos: answer yes/no for displaying photos of
        hotels
        :type display_hotel_photos : str
        """

        hotels_photos = None
        if hotels_details:
            reply_text = HandleSearchMsg._create_final_text(hotels_details)
            if display_hotel_photos == "no":
                for i_text in reply_text:
                    bot.send_message(chat_id, i_text)
            else:
                hotels_photos = HandleSearchMsg._extract_hotels_photos(hotels_details)
                reply_text_with_photo = HandleSearchMsg.create_final_text_with_photo(
                    reply_text, hotels_photos)
                for i_text in reply_text_with_photo:
                    bot.send_media_group(chat_id, i_text)
        else:
            reply_text = ("There is no available hotels as per your search settings."
                          "\nTry again with another search configuration.")
            bot.send_message(chat_id, reply_text,
                             reply_markup=start_inline_keyboard)
        HandleSearchMsg._save_final_response_in_db(user_id, reply_text,
                                                   hotels_photos)
        StateData.delete_state(chat_id, user_id)

    @staticmethod
    def _save_final_response_in_db(user_id: int, reply_text: Union[str, list[str]],
                                   hotels_photos: Optional[list[dict]]) -> None:
        """
        Saving reply text about hotels details in telegram_bot.db.

        :param user_id: User identifier
        :type user_id: int
        :param reply_text: text about hotel details which was sent to user
        :type reply_text: Union[str, list[str]
        :param hotels_photos: URLs of photos
        :type hotels_photos: Optional[list[dict]]
        :return:
        """

        save_data = {"reply_text": reply_text}
        if hotels_photos:
            save_data["hotels_photos"] = hotels_photos
        save_data = json.dumps(save_data)
        CrudDb.update_last_user_entry(db, History, user_id,
                                      History.bot_response, save_data)

    @staticmethod
    def _sort_user_search_settings(full_state_data: dict) -> str:
        """
        Sorting and making str with hotel search request details

        :param full_state_data: full user and his hotel search settings details
        :type full_state_data: dict

        :return: sorted hotel search request details
        :rtype: str
        """
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
                               "Price range: {min_price} - {max_price} per day in USD\n"
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
    def _extract_hotels_photos(hotels_details: list[dict]) -> list[list]:
        """
        Extracting  and return URls of hotels photos from hotels_details

        :param hotels_details: hotels details
        :type hotels_details: list[dict]
        :return: URls of hotels photos
        :rtype: list[list]
        """

        hotels_photos = list()
        for i_hotel in hotels_details:
            hotels_photos.append(i_hotel["photos_url"])
        return hotels_photos

    @staticmethod
    def _create_final_text(hotels_details: list[dict]) -> list[str]:
        """
        Creating list of strings with hotel information from hotels_details.

        :param hotels_details: hotels details
        :type hotels_details: list[dict]

        :return: hotels details
        :rtype: list[str]
        """

        reply_text = list()
        for i_hotel in hotels_details:
            reply_text.append(HandleSearchMsg._create_hotel_caption(i_hotel))
        return reply_text

    @staticmethod
    def _create_hotel_caption(i_hotel: dict) -> str:
        """
        Creating string with hotel information from dict i_hotel.

        :param i_hotel: hotel details
        :type i_hotel: dict

        :return: hotel details
        :rtype: str
        """

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
    def create_final_text_with_photo(reply_text: list[str],
                                     hotels_photos: list[list]) -> list[list[InputMediaPhoto]]:
        """
        Creating bot response message with photos. (Caption is required to group
        photos and text of hotel in one message block.)

        :param reply_text: text with hotel details
        :type reply_text: str
        :param hotels_photos: URls of hotels photos
        :type hotels_photos:  list[list]

        :return: hotel details
        :rtype:
        """

        reply_text_with_photos = list()
        hotels_amount = min(len(reply_text), len(hotels_photos))
        for index in range(hotels_amount):
            caption_count = 0
            temp_reply_text = list()
            for i_photo_url in hotels_photos[index]:
                if caption_count == 0:
                    photo_media = [InputMediaPhoto(media=i_photo_url,
                                                   caption=reply_text[index])]
                    caption_count += 1
                else:
                    photo_media = [InputMediaPhoto(media=i_photo_url)]
                temp_reply_text.extend(photo_media)
            reply_text_with_photos.append(temp_reply_text)
        return reply_text_with_photos

    @staticmethod
    def _check_eng_language(text: str) -> bool:
        """
        Checking if text contains only english lettres without digits and
        punctuation marks.

        :param text: any text
        :type text: str

        :return: True if contains only english letters else False
        :rtype: bool
        """

        a_latter = ord('a')
        z_latter = ord('z')
        for i_word in text.split(' '):
            for i_letter in i_word:
                if not a_latter <= ord(i_letter) <= z_latter:
                    return False
        return True

    @staticmethod
    def _extract_date_from_callback(call: CallbackQuery) -> Union[dict, bool]:
        """
        Extracting and returning date from calendar call if user pressed
        on day button on inline calendar else return False.

        :param call:
        :return: CallbackQuery
        :return: date | False
        :rtype: Union[dict, bool]
        """

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
        """
        Checking if date format (user_date) is existed and have correct
        format(%d.%m.%Y). Return exception message if raised during the
        above check else None.

        :param user_date: user input date
        :type user_date: str

        :return: exception message | None
        :rtype: Optional[str]
        """

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
        """
        Checking if check in date >= current date, return True.

        :param check_in_date: check in date
        :type check_in_date: dict

        :return: True | False
        :rtype: bool
        """

        converted_date = date(check_in_date["year"], check_in_date["month"],
                              check_in_date["day"])
        current_date = date.today()
        if converted_date >= current_date:
            return True
        else:
            return False

    @staticmethod
    def _valid_check_out_date(check_in_date: dict, check_out_date: dict) \
            -> bool:
        """
        Checking if check out date > check in date, return True.

        :param check_in_date:  check in date
        :type check_in_date: dict
        :param check_in_date:  check out date
        :type check_in_date: dict

        :return: True | False
        :rtype: bool
        """

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
        """
        Convert string to dict user date.

        :param user_date: user date
        :type user_date: str

        :return: user date
        :rtype: dict
        """
        user_date = user_date.split('.')
        user_date = {"day": int(user_date[0]),
                     "month": int(user_date[1]),
                     "year": int(user_date[2])}
        return user_date
