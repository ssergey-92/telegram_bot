from telebot import TeleBot, storage

from config_data.config import BOT_TOKEN


state_storage = storage.StateMemoryStorage()

bot = TeleBot(token=BOT_TOKEN, state_storage=state_storage)

