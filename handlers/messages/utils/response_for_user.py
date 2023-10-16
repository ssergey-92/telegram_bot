from handlers.sites_API.rapidapi_hotels import HotelsApi
from database.CRUD_interface import CrudDb
from database.history_model import History, db
from .state_data import delete_state
from .state_data import retrieve_full_state_data_by_id

from loader import bot
from telebot.types import InputMediaPhoto


def create_final_response(chat_id: int, user_id: int) -> None:   # to be modified when history handler is done
    full_state_data = retrieve_full_state_data_by_id(chat_id, user_id)
    CrudDb.update_last_user_entry(db, History, user_id, History.user_request,
                                  full_state_data)
    hotel_details = HotelsApi.find_hotels_in_city(chat_id, user_id)
    CrudDb.update_last_user_entry(db, History, user_id, History.bot_response,
                                  hotel_details)
    reply_text = create_response_text(hotel_details)
    if full_state_data["display_hotel_photos"] == "no":
        bot.send_message(chat_id, reply_text)
    else:
        send_response_with_photo(chat_id, reply_text, photos_url)
    delete_state(chat_id, user_id)


def create_response_text(hotel_details: list[dict]) -> str:
    pass
def send_response_with_photo(chat_id: int, hotel_details: list[dict]) -> None:
    bot.send_media_group(chat_id, [InputMediaPhoto(
        media="https://images.trvl-media.com/lodging/1000000/20000/15900/15838/c0137fe4.jpg?impolicy=resizecrop&rw=500&ra=fit",
        caption='Hotel info'),
        InputMediaPhoto(
            media="https://images.trvl-media.com/lodging/1000000/20000/15900/15838/20c5e07f.jpg?impolicy=resizecrop&rw=500&ra=fit"
        ),
        InputMediaPhoto(
            media="https://images.trvl-media.com/lodging/1000000/20000/15900/15838/a11eb569.jpg?impolicy=resizecrop&rw=500&ra=fit"
        )
    ])

