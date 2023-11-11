from datetime import datetime
from abc import ABC
import json
from telebot.types import InputMediaPhoto

from loader import bot
from states.history import HistoryStates
from .state_data import StateData
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard
from database.CRUD_interface import CrudDb
from database.history_model import History, db
from .search_state_messages import HandleSearchMsg


class HandleHistoryMsg(ABC):
    """
    Class HandleHistoryMsg. Parent class(abc.ABC)
    Class for handling history state messages.
    """

    @staticmethod
    def initialize_command(chat_id: int, user_id: int) -> None:
        """
        Handling history initialization command data from user.
        Deleting previous user state data if it exists, setting new history state and
        sending reply message.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        """

        StateData.delete_state(chat_id, user_id)
        bot.set_state(user_id, HistoryStates.records_number, chat_id)
        bot.send_message(chat_id, 'Select number of records 1 to 10:',
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def records_number(chat_id: int, user_id: int, required_records: str) -> None:
        """
        Handling user input data for records number state.
        If user input required_records as per input parameter, calling method
         _create_final_response to send existing history search data for current
          user. Other vice bot will send  message  with corrective action.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param required_records: quantity of records to show for previous
        hotel search
        :type required_records: int
        """

        required_records = required_records.strip('., ')
        if not required_records.isdigit():
            reply_text = "Use digits only to set number of records!\n(ex. 5)"
        elif int(required_records) == 0:
            reply_text = "Minimum number of records to display is 1!\n(ex. 1)"
        elif int(required_records) >= 11:
            reply_text = "Maximum number of records to display is 10!\n(ex. 10)"
        else:
            StateData.save_state_data_by_key(chat_id, user_id,
                                             "required_records", int(required_records))
            HandleHistoryMsg._create_final_response(chat_id, user_id,
                                                    int(required_records))
            return None
        bot.send_message(chat_id, reply_text,
                         reply_markup=cancel_reply_keyboard)

    @staticmethod
    def _create_final_response(chat_id: int, user_id: int,
                               required_records: int) -> None:
        """
        Sending user search history data.
        Sending notification message if there are less history records
        then user requested records.
        Sending only user request detail if search was canceled by user.
        Other vise calling _send_bot_response for sending bot response details.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int
        :param required_records: quantity of records to show for previous
        hotel search
        :type required_records: int
        """

        user_data = CrudDb.get_user_data(db, History, user_id, required_records,
                                         History.created_at, History.command,
                                         History.user_request, History.bot_response)
        records_found = len(user_data)
        if records_found < required_records:
            reply_text = ("There are {records_found} records in hotel search"
                          " history only!").format(
                records_found=records_found)
            bot.send_message(chat_id, reply_text)
        time_format = "%Y-%m-%d %H:%M:%S"
        for index in range(records_found):
            created_at = datetime.strftime(user_data[index]["created_at"],
                                           time_format)
            command_shortcut = user_data[index]["command"]
            user_request = user_data[index]["user_request"]
            bot_response = user_data[index]["bot_response"]
            if user_request != "Search was canceled by user":
                HandleHistoryMsg._send_bot_response(chat_id, created_at,
                                                    user_request, bot_response)
            else:
                reply_text = ("Created: {created_at}\n"
                              "Criteria: {command_shortcut}\n"
                              "{user_request}.\n").format(
                    created_at=created_at,
                    command_shortcut=command_shortcut,
                    user_request=user_request)
                bot.send_message(chat_id, reply_text)

    @staticmethod
    def _send_bot_response(chat_id: int, created_at: str, user_request: str,
                           bot_response: str) -> None:
        """
        Sending bot response data from history table in telegram_bot.db if hotel
        search request was without photos of hotel. Other vice the above data is
        used for recreating bot response message by
        HandleSearchMsg.create_final_text_with_photo and then send to user.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param created_at: time of creation user hotel search request
        :type created_at: str
        :param user_request: user  hotel search request details
        :type user_request: str
        :param bot_response: hotel details which were snd to user
        :type bot_response: str
        """

        reply_text_1 = ("Created: {created_at}\n"
                        "{user_request}.").format(
            created_at=created_at,
            user_request=user_request)
        bot.send_message(chat_id, reply_text_1)
        if bot_response == "not initialized":
            reply_text_2 = "Bot response: searched was canceled by user."
            bot.send_message(chat_id, reply_text_2)
        else:
            bot_response = json.loads(bot_response)
            if bot_response.get("hotels_photos"):
                reply_text_2 = HandleSearchMsg.create_final_text_with_photo(
                    bot_response["reply_text"], bot_response["hotels_photos"])
                for i_text in reply_text_2:
                    bot.send_media_group(chat_id, i_text)
            elif isinstance(bot_response["reply_text"], list):  # hotels data without photo
                for i_text in bot_response["reply_text"]:
                    bot.send_message(chat_id, i_text)
            else:  # hotels were not found
                bot.send_message(chat_id, bot_response["reply_text"])
