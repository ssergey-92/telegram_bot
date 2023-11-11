from telebot import TeleBot, storage

from config_data.config import BOT_TOKEN

"""Creating state storage for multiuser mode and setting 
telegram bot base settings"""

state_storage = storage.StateMemoryStorage()
bot = TeleBot(token=BOT_TOKEN, state_storage=state_storage)
