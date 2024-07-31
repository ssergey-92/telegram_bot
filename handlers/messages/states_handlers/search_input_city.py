"""Module for handling input_city state.

Contains common handling functions to handle input city name from message
for CustomSearchStates, LuxurySearchStates and BudgetSearchStates scenarios.
"""

from telebot.handler_backends import State

from handlers.sites_API.rapidapi_hotels import HotelsApi
from handlers.messages.utils.state_data import StateData
from keyboards.inline.search_cities import get_search_city_inline_keyboard
from keyboards.reply.cancel import cancel_reply_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

msg_city_found = "You mean:"
msg_city_not_found = (
    "Sorry, there is no city '{city_name}' in our database.\nTry to enter "
    "proper city name or use another place.\nRussia is not supported!"
)
msg_use_eng_words = "Enter city name using ENGLISH letters only!\n(ex. Miami)"
state_data = {"input_city": "", "found_cities": []}


def is_eng_letters(text: str) -> bool:
    """ Check that text contains english lettres, spaces and punctuation.

    Args:
        text (str): text to check.

    Returns:
        bool: True if text contains english lettres, spaces and punctuation
            otherwise False.

    """
    bot_logger.debug(f"{text=}")
    stripped_text = text.strip(",. ").replace(",", "").lower()
    a_latter = ord("a")
    z_latter = ord("z")
    for i_word in stripped_text.split(" "):
        for i_letter in i_word:
            if not a_latter <= ord(i_letter) <= z_latter:
                return False
    return True


def handle_input_city(
    chat_id: int, user_id: int, city_name: str, next_state: State,
) -> None:
    """Handle user input data for search city name.

    If user input city name consists of english letters only, then search city.
    If city is found then save the above data in bot state storage, set next
    state(new_state) and send message for next state.
    Other vice bot sends  message  with corrective action.

    Args:
        chat_id (int): chat identifier
        user_id (int): user identifier
        city_name (str): input city name
        next_state (State): next state

    """
    reply_markup = cancel_reply_keyboard
    if is_eng_letters(city_name):
        found_cities = HotelsApi.find_city(user_id, city_name)
        if found_cities:
            reply_msg = msg_city_found
            bot.set_state(user_id, next_state, chat_id)
            state_data["input_city"] = city_name
            state_data["found_cities"] = found_cities
            StateData.save_multiple_user_data(chat_id, user_id, state_data)
            reply_markup = get_search_city_inline_keyboard(found_cities)
        else:
            reply_msg = msg_city_not_found.format(city_name=city_name)
    else:
        reply_msg = msg_use_eng_words
    bot_logger.debug(f"{chat_id=}, {user_id=}, {city_name=}, {reply_msg=}")
    bot.send_message(chat_id, reply_msg, reply_markup=reply_markup)
