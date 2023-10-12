from telebot.types import CallbackQuery

from loader import bot
from .start import reply_msg_start
from .cancel_search import reply_msg_cancel_search
from .help import reply_msg_help
from .top_budget_hotels import reply_msg_low_price
from config_data.config import BOT_COMMANDS


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.data == BOT_COMMANDS[0][0]:     # /start
        reply_msg_start(call.message.chat.id, call.from_user.full_name)
    elif call.data == BOT_COMMANDS[1][0]:     # /cancel_search
        reply_msg_cancel_search(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[2][0]:     # /help
        reply_msg_help(call.message.chat.id)
    elif call.data == BOT_COMMANDS[3][0]:       # /low_price
        reply_msg_low_price(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[4][0]:      # /high_price
        pass
    elif call.data == BOT_COMMANDS[5][0]:      # /best_deal
        pass
    elif call.data == BOT_COMMANDS[6][0]:      # /history
        pass

# ("start", "Start Bot", "Launching the bot."),
#  ("cancel_search", "Cancel Current Search",
#   "Cancel current search state. Back to main menu"),
#  ("help", "Help", "Bot commands and shortcuts description."),
#  ("low_price", "Top Budget Hotels",
#   "List of the most cheapest hotels in selected city."),
#  ("high_price", "Top Luxury Hotels",
#   "List of the most expensive hotels in selected city."),
#  ("best_deal", "Custom Hotel Search",
#   "Hotel search as per custom preferences."),
#  ("history", "History", "Hotel search history.")
# )
