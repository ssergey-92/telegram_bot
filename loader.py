"""Module to init telegram bot, state storage, db, load .env and handlers

Package import sequence is important.
"""

from os import getenv

from telebot import TeleBot, storage

import config_data.config
import database.history_model

"""Create state storage for multiuser mode and set bot base settings"""
state_storage = storage.StateMemoryStorage()
bot = TeleBot(token=getenv("BOT_TOKEN"), state_storage=state_storage)
