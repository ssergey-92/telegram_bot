from os import getenv
from sys import exit
from dotenv import load_dotenv, find_dotenv

if find_dotenv():
    load_dotenv()
    BOT_TOKEN = getenv('BOT_TOKEN')
    RAPID_API_KEY = getenv('RAPID_API_KEY')
else:
    exit('File .env is not found.')

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



