from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_data.config import BOT_TOKEN


state_storage = StateMemoryStorage()

bot = TeleBot(token=BOT_TOKEN, state_storage=state_storage)

