from datetime import date

from telebot.types import Message, CallbackQuery
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from loader import bot
from states.budget_search import BudgetSearchStates
from config_data.config import BOT_COMMANDS
from .handle_state_messages import HandleMsg

low_price_cmd = BOT_COMMANDS[3][0]
low_price_shortcut = BOT_COMMANDS[3][1]


@bot.message_handler(commands=[low_price_cmd])
def low_price_command(message: Message) -> None:
    reply_msg_low_price(message.chat.id, message.from_user.id)


def reply_msg_low_price(chat_id: int, user_id: int) -> None:
    HandleMsg.initialize_command(chat_id, user_id, low_price_shortcut,
                                 "PRICE_LOW_TO_HIGH",
                                 1, 1000000,
                                 BudgetSearchStates.input_city)


@bot.message_handler(state=BudgetSearchStates.input_city)
def budget_input_city_state(message: Message) -> None:
    HandleMsg.input_city(message.chat.id, message.from_user.id,
                         message.text, low_price_shortcut,
                         BudgetSearchStates.confirm_city)


@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_callback(call: CallbackQuery):
    reply_text = "Select check in date:"
    now = date.today()
    reply_markup = generate_calendar_days(year=now.year,
                                          month=now.month)
    HandleMsg.confirm_city(call.message.chat.id, call.from_user.id,
                           BudgetSearchStates.check_in_date,
                           BudgetSearchStates.input_city, reply_text, call.data,
                           reply_markup)


@bot.message_handler(state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_msg(message: Message) -> None:
    HandleMsg.confirm_city(message.chat.id, message.from_user.id,
                           BudgetSearchStates.check_in_date,
                           BudgetSearchStates.input_city)


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
                            state=BudgetSearchStates.check_in_date)
def budget_check_in_date_state_cb(call: CallbackQuery) -> None:
    check_in_date = HandleMsg.check_calendar_callback(call)
    if check_in_date:
        HandleMsg.check_in(call.message.chat.id, call.from_user.id,
                           check_in_date, BudgetSearchStates.check_out_date)


@bot.message_handler(state=BudgetSearchStates.check_in_date)
def budget_check_in_date_state_msg(message: Message) -> None:
    check_in_date = HandleMsg.check_calendar_message(message)
    if check_in_date:
        HandleMsg.check_in(message.chat.id, message.from_user.id,
                           check_in_date, BudgetSearchStates.check_out_date)


@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_cb(call: CallbackQuery) -> None:
    check_out_date = HandleMsg.check_calendar_callback(call)
    if check_out_date:
        HandleMsg.check_out(call.message.chat.id, call.from_user.id,
                            check_out_date, BudgetSearchStates.travellers)


@bot.message_handler(state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_msg(message: Message) -> None:
    check_out_date = HandleMsg.check_calendar_message(message)
    if check_out_date:
        HandleMsg.check_out(message.chat.id, message.from_user.id,
                            check_out_date, BudgetSearchStates.travellers)


@bot.message_handler(state=BudgetSearchStates.travellers)
def budget_travellers_state(message: Message) -> None:
    HandleMsg.set_travellers(message.chat.id, message.from_user.id,
                             message.text, BudgetSearchStates.hotels_amount)


@bot.message_handler(state=BudgetSearchStates.hotels_amount)
def budget_hotel_amount_state(message: Message) -> None:
    HandleMsg.set_hotel_amount(message.chat.id, message.from_user.id,
                               message.text, BudgetSearchStates.hotels_photo)


@bot.message_handler(state=BudgetSearchStates.hotels_photo)
def budget_photo_state(message: Message) -> None:
    HandleMsg.show_hotel_photo(message.chat.id, message.from_user.id,
                               message.text, BudgetSearchStates.hotels_photo_amount)


@bot.message_handler(state=BudgetSearchStates.hotels_photo_amount)
def budget_photo_amount_state(message: Message) -> None:
    HandleMsg.set_photos_amount(message.chat.id, message.from_user.id,
                                message.text)
