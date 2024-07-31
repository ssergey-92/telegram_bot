"""Module with config data for telegram bot."""

from os import getenv
from sys import exit

from dotenv import load_dotenv, find_dotenv

BOT_NAME = "Hotel Data Provider"
START_COMMAND_DATA = {
    "command": "start",
    "shortcut": "Start Bot",
    "description": f"Launching {BOT_NAME} bot.",
}
CANSEL_SEARCH_COMMAND_DATA = {
    "command": "cancel_search",
    "shortcut": "Cancel Current Search",
    "description": "Cancel current search state. Back to main menu",
}
HELP_COMMAND_DATA = {
    "command": "help",
    "shortcut": "Help",
    "description": "Bot commands and shortcuts description.",
}
LOW_PRICE_COMMAND_DATA = {
    "command": "low_price",
    "shortcut": "Top Budget Hotels",
    "description": "List of the cheapest hotels in selected city.",
}
HIGH_PRICE_COMMAND_DATA = {
    "command": "high_price",
    "shortcut": "Top Luxury Hotels",
    "description": "List of the most expensive hotels in selected city.",
}
BEST_DEALS_COMMAND_DATA = {
    "command": "best_deal",
    "shortcut": "Custom Hotel Search",
    "description": "Hotel search as per custom preferences.",
}
HISTORY_COMMAND_DATA = {
    "command": "history",
    "shortcut": "History search",
    "description": "Hotel search history.",
}
BOT_COMMANDS = {
    "main": [
        START_COMMAND_DATA, CANSEL_SEARCH_COMMAND_DATA, HELP_COMMAND_DATA,
    ],
    "hotel_search": [
        LOW_PRICE_COMMAND_DATA,
        HIGH_PRICE_COMMAND_DATA,
        BEST_DEALS_COMMAND_DATA,
    ],
    "history": [HISTORY_COMMAND_DATA],
}


def load_env_data() -> None:
    """Load .env data and add to os environment.

    If .env or required keys are not found call system exit func.

    """

    error_text = "File .env is not found."
    if not find_dotenv():
        error_text = ".env is not found."
    else:
        load_dotenv()
        if not getenv("BOT_TOKEN"):
            error_text = "BOT TOKEN is not found."
        elif not getenv("RAPID_API_KEY"):
            error_text = "RAPID API KEY is not found."
        elif not getenv("LOGS_FILE_NAME"):
            error_text = "Logs files name is not found"
        else:
            return
    exit(error_text)


load_env_data()
