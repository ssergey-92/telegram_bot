from datetime import date

from telebot.types import Message, CallbackQuery
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from loader import bot
from states.luxury_search import LuxurySearchStates
from config_data.config import BOT_COMMANDS
from .handle_state_messages import HandleMsg

high_price_cmd = BOT_COMMANDS[4][0]
high_price_shortcut = BOT_COMMANDS[4][1]


@bot.message_handler(commands=[high_price_cmd])
def high_price_command(message: Message) -> None:
    reply_msg_high_price(message.chat.id, message.from_user.id)


def reply_msg_high_price(chat_id: int, user_id: int) -> None:
    HandleMsg.initialize_command(chat_id, user_id, high_price_shortcut,
                                 "PRICE_LOW_TO_HIGH",
                                 1, 1000000,
                                 LuxurySearchStates.input_city)


@bot.message_handler(state=LuxurySearchStates.input_city)
def luxury_input_city_state(message: Message) -> None:
    HandleMsg.input_city(message.chat.id, message.from_user.id,
                         message.text, high_price_shortcut,
                         LuxurySearchStates.confirm_city)


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.confirm_city)
def luxury_confirm_city_state_callback(call: CallbackQuery):
    reply_text = "Select check in date:"
    now = date.today()
    reply_markup = generate_calendar_days(year=now.year,
                                          month=now.month)
    HandleMsg.confirm_city(call.message.chat.id, call.from_user.id,
                           LuxurySearchStates.check_in_date,
                           LuxurySearchStates.input_city, reply_text, call.data,
                           reply_markup)


@bot.message_handler(state=LuxurySearchStates.confirm_city)
def luxury_confirm_city_state_msg(message: Message) -> None:
    HandleMsg.confirm_city(message.chat.id, message.from_user.id,
                           LuxurySearchStates.check_in_date,
                           LuxurySearchStates.input_city)


@bot.callback_query_handler(func=None,
                            calendar_config=calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery) -> None:
    callback_data: dict = calendar_factory.parse(callback_data=call.data)
    year, month = int(callback_data['year']), int(callback_data['month'])

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_days(year=year,
                                                                      month=month))


@bot.callback_query_handler(func=None,
                            calendar_zoom_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery) -> None:
    callback_data: dict = calendar_zoom.parse(callback_data=call.data)
    year = int(callback_data.get('year'))

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_months(year=year))


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.check_in_date)
def luxury_check_in_date_state_cb(call: CallbackQuery) -> None:
    check_in_date = HandleMsg.check_calendar_callback(call)
    if check_in_date:
        HandleMsg.check_in(call.message.chat.id, call.from_user.id,
                           check_in_date, LuxurySearchStates.check_out_date)


@bot.message_handler(state=LuxurySearchStates.check_in_date)
def luxury_check_in_date_state_msg(message: Message) -> None:
    check_in_date = HandleMsg.check_calendar_message(message)
    if check_in_date:
        HandleMsg.check_in(message.chat.id, message.from_user.id,
                           check_in_date, LuxurySearchStates.check_out_date)


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.check_out_date)
def luxury_check_out_date_state_cb(call: CallbackQuery) -> None:
    check_out_date = HandleMsg.check_calendar_callback(call)
    if check_out_date:
        HandleMsg.check_out(call.message.chat.id, call.from_user.id,
                            check_out_date, LuxurySearchStates.travellers)


@bot.message_handler(state=LuxurySearchStates.check_out_date)
def luxury_check_out_date_state_msg(message: Message) -> None:
    check_out_date = HandleMsg.check_calendar_message(message)
    if check_out_date:
        HandleMsg.check_out(message.chat.id, message.from_user.id,
                            check_out_date, LuxurySearchStates.travellers)


@bot.message_handler(state=LuxurySearchStates.travellers)
def luxury_travellers_state(message: Message) -> None:
    HandleMsg.set_travellers(message.chat.id, message.from_user.id,
                             message.text, LuxurySearchStates.hotels_amount)


@bot.message_handler(state=LuxurySearchStates.hotels_amount)
def luxury_hotel_amount_state(message: Message) -> None:
    HandleMsg.set_hotel_amount(message.chat.id, message.from_user.id,
                               message.text, LuxurySearchStates.hotels_photo)


@bot.message_handler(state=LuxurySearchStates.hotels_photo)
def luxury_photo_state(message: Message) -> None:
    HandleMsg.show_hotel_photo(message.chat.id, message.from_user.id,
                               message.text, LuxurySearchStates.hotels_photo_amount)


@bot.message_handler(state=LuxurySearchStates.hotels_photo_amount)
def luxury_photo_amount_state(message: Message) -> None:
    HandleMsg.set_photos_amount(message.chat.id, message.from_user.id,
                                message.text)
