from telebot.types import CallbackQuery

from loader import bot
from .start_cmd import reply_msg_start
from .cancel_search_cmd import reply_msg_cancel_search
from .help_cmd import reply_msg_help
from .top_budget_hotels_state import reply_msg_low_price
from .top_luxury_hotels_state import reply_msg_high_price
from .custom_hotel_search_state import reply_msg_best_deal
from .history_state import reply_msg_history
from config_data.config import BOT_COMMANDS


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery) -> None:
    """
    Catching unstated incoming callback query from a callback button in an
    inline keyboard and calling appropriate function according to bot commands.

    :param call:  user reply data from inline keyboard
    :type call: CallbackQuery
    """

    if call.data == BOT_COMMANDS[0][0]:  # /start
        reply_msg_start(call.message.chat.id, call.from_user.id,
                        call.from_user.full_name)
    elif call.data == BOT_COMMANDS[1][0]:  # /cancel_search
        reply_msg_cancel_search(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[2][0]:  # /help
        reply_msg_help(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[3][0]:  # /low_price
        reply_msg_low_price(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[4][0]:  # /high_price
        reply_msg_high_price(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[5][0]:  # /best_deal
        reply_msg_best_deal(call.message.chat.id, call.from_user.id)
    elif call.data == BOT_COMMANDS[6][0]:  # /history
        reply_msg_history(call.message.chat.id, call.from_user.id)
