from handlers.sites_API.rapidapi_hotels import HotelsApi
from database.CRUD_interface import CrudDb
from database.history_model import History, db
from .state_data import delete_state
from .state_data import retrieve_full_state_data_by_id

from loader import bot
from telebot.types import InputMediaPhoto
from config_data.config import BOT_COMMANDS


def send_final_response(chat_id: int, user_id: int) -> None:  # to be modified when history handler is done
    full_state_data = retrieve_full_state_data_by_id(chat_id, user_id)
    user_request_details = sort_user_request_details(full_state_data)
    bot.send_message(chat_id, user_request_details)
    CrudDb.update_last_user_entry(db, History, user_id, History.user_request,
                                  user_request_details)
    bot.send_message(chat_id,"searching suitable hotels")
    hotel_details = HotelsApi.find_hotels_in_city(chat_id, user_id)
    if full_state_data["display_hotel_photos"] == "no":
        reply_text = create_final_text(hotel_details)
        for i_text in reply_text:
            bot.send_message(chat_id)
    else:
        reply_text = create_final_text_with_photo(hotel_details)
        for i_text in reply_text:
            bot.send_media_group(chat_id, i_text)
    CrudDb.update_last_user_entry(db, History, user_id, History.bot_response,
                                  reply_text)
    delete_state(chat_id, user_id)


def sort_user_request_details(full_state_data: dict) -> str:
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
    if full_state_data["command"] == BOT_COMMANDS[5][1]:  # best_deal(custom search)
        request_details = ("{request_details}\n"
                           "Min price: {min_price}\n"
                           "Max price: {max_price}").format(
            request_details=request_details,
            min_price=full_state_data["min_price"],
            max_price=full_state_data["max_price"])
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


def create_final_text(hotel_details: list[dict]) -> list[str]:
    reply_text = list()
    for i_hotel in hotel_details:
        reply_text.append(create_hotel_signature(i_hotel))
    return reply_text


def create_hotel_signature(i_hotel: dict) -> str:
    hotel_signature = ("Name: {hotel_name}\n"
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

    return hotel_signature


def create_final_text_with_photo(hotel_details: list[dict]) \
        -> list[list[InputMediaPhoto]]:
    reply_text_with_photos = list()
    for i_hotel in hotel_details:
        hotel_signature = create_hotel_signature(i_hotel)
        caption_count = 0
        temp_reply_text = list()
        for i_photo_url in i_hotel["photos_url"]:
            if caption_count == 0:
                photo_media = [InputMediaPhoto(media=i_photo_url, caption=hotel_signature)]
                caption_count += 1
            else:
                photo_media = [InputMediaPhoto(media=i_photo_url)]
            temp_reply_text.extend(photo_media)
        reply_text_with_photos.append(temp_reply_text)
    return reply_text_with_photos



