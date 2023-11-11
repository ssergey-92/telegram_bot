from os import getenv
from sys import exit
from typing import Optional

from dotenv import load_dotenv, find_dotenv

BOT_COMMANDS = (
    ("start", "Start Bot", "Launching the bot."),
    ("cancel_search", "Cancel Current Search",
     "Cancel current search state. Back to main menu"),
    ("help", "Help", "Bot commands and shortcuts description."),
    ("low_price", "Top Budget Hotels",
     "List of the cheapest hotels in selected city."),
    ("high_price", "Top Luxury Hotels",
     "List of the most expensive hotels in selected city."),
    ("best_deal", "Custom Hotel Search",
     "Hotel search as per custom preferences."),
    ("history", "History", "Hotel search history.")
)


def get_bot_token_apikey() -> Optional[tuple[str, str]]:
    """
    Searching and retrieving BOT_TOKEN, RAPID_API_KEY form env file.
    If BOT_TOKEN or RAPID_API_KEY is not found, program will be  canceled.


    :return : (BOT_TOKEN, RAPID_API_KEY) | None
    :rtype: Optional[tuple[str, str]]
    """

    error_text = "File .env is not found."
    if find_dotenv():
        load_dotenv()
        BOT_TOKEN = getenv("BOT_TOKEN")
        RAPID_API_KEY = getenv("RAPID_API_KEY")
        if not BOT_TOKEN:
            error_text = "BOT TOKEN is not found."
        elif not RAPID_API_KEY:
            error_text = "RAPID API KEY is not found."
        else:
            return BOT_TOKEN, RAPID_API_KEY
    exit(error_text)


BOT_TOKEN, RAPID_API_KEY = get_bot_token_apikey()
