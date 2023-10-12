from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config


state_storage = StateMemoryStorage()

bot = TeleBot(token=config.BOT_TOKEN, state_storage=state_storage)

