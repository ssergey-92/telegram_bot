"""Module to search hotels as per user search settings and sending response.

Module handle searching hotels and sending response if all states successfully
completed in  CustomSearchStates, LuxurySearchStates and BudgetSearchStates
scenarios.
"""

from json import dumps

from telebot.types import InputMediaPhoto

from config_data.config import BEST_DEALS_COMMAND_DATA
from database.crud_history_interface import HistoryCRUD
from database.history_model import History
from handlers.messages.utils.state_data import StateData
from handlers.sites_API.rapidapi_hotels import HotelsApi
from keyboards.inline.start import start_inline_keyboard
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_commence_search = "searching suitable hotels"
msg_hotels_not_found = (
    "There is no available hotels as per your search settings."
    "\nTry again with another search configuration."
)
hotel_search_settings_common_1 = (
    "Search settings:\n\n"
    "Criteria: {command_shortcut}\n"
    "City: {city}\n"
    "Check in date: {ci_day}.{ci_month}.{ci_year}\n"
    "Check out date: {co_day}.{co_month}.{co_year}\n"
)
hotel_search_settings_best_deal = (
    "Price range: {min_price} - {max_price} per day in USD\n"
    "Distance range: {min_distance} - {max_distance} MILE\n"
        )
hotel_search_settings_common_2 = (
    "Travellers: {travellers}\n"
    "Hotels: {hotels_amount}\n"
    "Hotel photos: {display_hotel_photos}"
)
hotel_search_settings_optional_part = "\nPhotos: {hotel_photo_amount}"
hotel_caption = (
    "Name: {hotel_name}\n"
    "Price per day: {price_per_day}\n"
    "Price per stay: {price_per_stay}\n"
    "Rating: {rating}/5\n"
    "Distance from city center: {distance}\n"
    "Address: {hotel_address}\n"
    "Website: {site_url}"
)


def create_search_settings_msg(user_state_data: dict) -> str:
    """Create hotel search settings msg from user full state data.

    Args:
        user_state_data (dict): full user state data

    Returns:
        str: search settings msg

    """
    msg_part_1 = hotel_search_settings_common_1.format(
        command_shortcut=user_state_data["command"],
        city=user_state_data["full_name"],
        ci_day=user_state_data["check_in_date"]["day"],
        ci_month=user_state_data["check_in_date"]["month"],
        ci_year=user_state_data["check_in_date"]["year"],
        co_day=user_state_data["check_out_date"]["day"],
        co_month=user_state_data["check_out_date"]["month"],
        co_year=user_state_data["check_out_date"]["year"],
    )
    if user_state_data["command"] == BEST_DEALS_COMMAND_DATA["shortcut"]:
        best_deals_specific_settings = hotel_search_settings_best_deal.format(
            min_price=user_state_data["min_price"],
            max_price=user_state_data["max_price"],
            min_distance=user_state_data["min_distance"],
            max_distance=user_state_data["max_distance"],
        )
        msg_part_1 += best_deals_specific_settings
    msg_part_2 = hotel_search_settings_common_2.format(
        travellers=user_state_data["adults"],
        hotels_amount=user_state_data["hotels_amount"],
        display_hotel_photos=(
            "Yes" if user_state_data["display_hotel_photos"] else "No"
        )
    )
    if user_state_data["display_hotel_photos"]:
        optional_search_settings = hotel_search_settings_optional_part.format(
            hotel_photo_amount=user_state_data["hotel_photo_amount"],
        )
        msg_part_2 += optional_search_settings
    search_settings_msg = msg_part_1 + msg_part_2
    bot_logger.debug(f"{user_state_data=}, {search_settings_msg=}")
    return search_settings_msg


def create_hotel_caption(hotel_details: dict) -> str:
    """Create hotel caption.

    Args:
        hotel_details (dict): hotel details

    Returns
        str: hotel caption

    """
    specific_hotel_caption = hotel_caption.format(
        hotel_name=hotel_details["name"],
        price_per_day=hotel_details["price_per_day"],
        price_per_stay=hotel_details["price_per_stay"],
        rating=hotel_details["hotel_rating"],
        distance=hotel_details["distance"],
        hotel_address=hotel_details["hotel_address"],
        site_url=hotel_details["site_url"],
    )
    bot_logger.debug(f"{hotel_details=}, {specific_hotel_caption=}")
    return specific_hotel_caption


def sort_hotels_details_for_response(
        hotels_details: list[dict], required_photos: bool = False,
) -> list[dict]:
    """Sort hotels details for response to user.

    Create hotel caption and include hotel photos if required.

    Args:
        hotels_details (list[dict]): hotel details
        required_photos (bool): include or exclude hotel photos

    Returns:
        list[dict]: hotels details to send

    """
    hotels_details_to_send = list()
    for i_hotel in hotels_details:
        i_hotel_details_to_send = {"caption": create_hotel_caption(i_hotel)}
        if required_photos:
            i_hotel_details_to_send["photos"] = i_hotel["photos_url"]
        hotels_details_to_send.append(i_hotel_details_to_send)
    bot_logger.debug(
        f"{hotels_details=}, {required_photos=}, {hotels_details_to_send=}",
    )
    return hotels_details_to_send


def create_photo_media_msgs_for_hotels(
        sorted_hotels_details: list[dict],
) -> list[list[InputMediaPhoto]]:
    """Create media messages with hotel caption and photos.

    Args:
        sorted_hotels_details (list[dict]): sorted hotel details prepared for
            response

    Returns:
        list[list[InputMediaPhoto]]: media msgs with hotel details

    """
    media_msgs = []
    for i_hotel in sorted_hotels_details:
        i_hotel_media_photos = [
            InputMediaPhoto(
                media=i_hotel["photos"][0], caption=i_hotel["caption"],
            )
        ]
        for photos_index in range(1, len(i_hotel["photos"])):
            photo_media = InputMediaPhoto(
                media=i_hotel["photos"][photos_index],
            )
            i_hotel_media_photos.append(photo_media)
        media_msgs.append(i_hotel_media_photos)
    bot_logger.debug(f"{sorted_hotels_details=}, {media_msgs=}")
    return media_msgs


def send_hotels_details(
        chat_id: int,
        sorted_hotels_details: list[dict],
        display_hotel_photos: bool,
) -> None:
    """Send hotels details to user.

    Args:
        chat_id (int): chat identifier
        sorted_hotels_details (list[dict]): sorted hotel details prepared for
            response
        display_hotel_photos (bool): display hotel photos

    """
    bot_logger.debug(f"{sorted_hotels_details=}, {display_hotel_photos=}")
    if display_hotel_photos:
        media_reply_msgs = create_photo_media_msgs_for_hotels(
            sorted_hotels_details,
        )
        for i_media_msg in media_reply_msgs:
            bot.send_media_group(chat_id, i_media_msg)
    else:
        for i_hotel_details in sorted_hotels_details:
            bot.send_message(chat_id, i_hotel_details["caption"])


def send_commence_search_msgs(chat_id: int, user_search_settings: str) -> None:
    """Send selected user search settings and commence search msgs to use.

    Args:
        chat_id (int): chat identifier
        user_search_settings (str): user search settings

    """
    bot_logger.debug(f"{chat_id=}, {user_search_settings=}")
    bot.send_message(chat_id, user_search_settings)
    bot.send_message(
        chat_id, msg_commence_search, reply_markup=cancel_reply_keyboard,
    )


def handle_hotel_search(chat_id: int, user_id: int) -> None:
    """Find hotels as per user search settings, save data and send response.

    Send response and save data if user did not cancel search state.

    Args:
        chat_id (int): chat identifier
        user_id (int) : User identifier

    """
    bot_logger.debug(f"{chat_id=}, {user_id=}")
    user_state_data = StateData.get_full_user_data(chat_id, user_id)
    search_settings = create_search_settings_msg(user_state_data)
    HistoryCRUD.update_field_by_id(
        user_state_data["history_id"], History.user_request, search_settings,
    )
    send_commence_search_msgs(chat_id, search_settings)
    found_hotels = HotelsApi.find_hotels_in_city(chat_id, user_id)
    if StateData.get_user_data_by_key(chat_id, user_id, "commence_search"):
        if found_hotels:
            sorted_hotels_details = sort_hotels_details_for_response(
                found_hotels, user_state_data["display_hotel_photos"],
            )
            send_hotels_details(
                chat_id,
                sorted_hotels_details,
                user_state_data["display_hotel_photos"]
            )
            bot_response = dumps(sorted_hotels_details)
        else:
            reply_msg = msg_hotels_not_found
            bot.send_message(
                chat_id, reply_msg, reply_markup=start_inline_keyboard,
            )
            bot_response = [{"caption": reply_msg}]
        HistoryCRUD.update_field_by_id(
            user_state_data["history_id"], History.bot_response, bot_response,
        )
        bot_logger.debug(f"{chat_id=}, {user_id=}, {bot_response=}")
    StateData.delete_state(chat_id, user_id)
