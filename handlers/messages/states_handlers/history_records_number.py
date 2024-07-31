"""Module for handling state History.records_numbers."""

from datetime import datetime
import json

from .common import get_int_number
from .search_result import send_hotels_details
from database.crud_history_interface import HistoryCRUD
from keyboards.inline.start import start_inline_keyboard
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot


min_records = 1
max_records = 10
msg_searching_records = "Searching history records!\nkindly wait!"
msg_use_digits = "Use digits only to set number of records!\n(ex. 3)"
msg_max_allowed_records_number = (
    "Maximum number of records to display is {max_records}!"
    "\n(ex. {max_records})".format(max_records=max_records)
)
msg_min_allowed_records_number = (
    "Minimum number of records to display is {min_records}!"
    "\n(ex. {min_records})".format(min_records=min_records)
)
msg_no_records_found = (
    "History records are not found!\nPerform at least 1 hotel search!"
)
msg_less_records_found = (
    "There are {records_found} records in hotel search history!"
)
msg_found_history_records = "Kindly see found history records"
msg_bot_response_canceled = "Bot response: searched was canceled by user."
history_search_header = "Created: {created_at}\n{user_request}"


def send_history_search_header(chat_id: int, history_record: dict) -> None:
    """Send msg with user search settings details.

    Args:
        chat_id (int): chat id.
        history_record (dict): history record entry.

    """
    record_created_at = datetime.strftime(
        history_record["created_at"], "%Y-%m-%d %H:%M:%S",
    )
    reply_msg = history_search_header.format(
            created_at=record_created_at,
            user_request=history_record["user_request"],
    )
    bot.send_message(chat_id, reply_msg)


def send_processed_response(chat_id: int, history_record: dict) -> None:
    """Send result of hotel search from history record to user.

    Args:
        chat_id (int): chat id.
        history_record (dict): history record entry.
    """

    if history_record["bot_response"] == "not initialized":
        reply_msg = msg_bot_response_canceled
        bot.send_message(chat_id, reply_msg)
    else:
        hotels_details: list[dict] = json.loads(history_record["bot_response"])
        display_photos = True if hotels_details[0].get("photos") else False
        send_hotels_details(chat_id, hotels_details, display_photos)


def send_history_records(
    chat_id: int, user_id: int, required_records: int,
) -> None:
    """Send user's search history records details.

    Send msg if found history records are less then requested records or not
    found. Then send hotel search result from history records.

    Args:
        chat_id (int): chat id.
        user_id (int): user id.
        required_records (int): number of records to show.

    """
    bot.send_message(chat_id, msg_searching_records)
    found_records = HistoryCRUD.get_latest_user_entries(
        user_id, required_records,
    )
    total_found_records = len(found_records)
    if not total_found_records:
        reply_msg = msg_no_records_found
        bot.send_message(
            chat_id, reply_msg, reply_markup=start_inline_keyboard,
        )
    else:
        if total_found_records < required_records:
            reply_msg = msg_less_records_found.format(
                records_found=total_found_records,
            )
            bot.send_message(
                chat_id, reply_msg, reply_markup=cancel_reply_keyboard,
            )
        for index, i_record in enumerate(found_records, 1):
            bot.send_message(chat_id, f"*****Record # {index }******")
            send_history_search_header(chat_id, i_record)
            if i_record["user_request"] != "Search was canceled by user":
                send_processed_response(chat_id, i_record)


def handle_records_number(
        chat_id: int, user_id: int, required_records: str,
) -> None:
    """Handle user input required records for History records number state.

    If required_records as per  format (digit[min_records:max_records]), call
    handling func to send history records
    Other vice bot will send  message  with corrective action.

    Args:
        chat_id (int): chat id.
        user_id (int): user id.
        required_records (str): number of records to show.

    """
    required_records = get_int_number(required_records)
    if not required_records and required_records != 0:
        reply_text = msg_use_digits
    elif required_records < min_records:
        reply_text = msg_min_allowed_records_number
    elif required_records > max_records:
        reply_text = msg_max_allowed_records_number
    else:
        send_history_records(chat_id, user_id, required_records)
        return
    bot.send_message(
        chat_id, reply_text, reply_markup=cancel_reply_keyboard,
    )
