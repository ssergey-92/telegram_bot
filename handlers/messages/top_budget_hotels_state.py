from typing import Union, Callable
from datetime import date
from telebot.types import (Message, CallbackQuery, InlineKeyboardMarkup)

from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from keyboards.inline_keyboard.search_cities import (
    create_search_city_inline_keyboard)
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard
from database.history_model import History, db
from database.CRUD_interface import CrudDb
from loader import bot
from states.BudgetSearch import BudgetSearchStates
from config_data.config import BOT_COMMANDS
from .utils.state_data import StateData
from .utils.date_handling import (extract_date, valid_check_in_date,
                                  check_date_format, valid_check_out_date,
                                  convert_str_date_to_dict)

from .utils.response_for_user import send_final_response
from handlers.sites_API.rapidapi_hotels import HotelsApi
from .handle_messages import HandleMsg


low_price_cmd = BOT_COMMANDS[3][0]
low_price_shortcut = BOT_COMMANDS[3][1]


@bot.message_handler(commands=[low_price_cmd])
def low_price_command(message: Message) -> None:
    print(type(message), message.__class__)
    reply_msg_low_price(message.chat.id, message.from_user.id)


def reply_msg_low_price(chat_id: int, user_id: int) -> None:
    HandleMsg.initialize_command(chat_id, user_id, low_price_shortcut,
                                 "PRICE_LOW_TO_HIGH",
                                 1, 1000000, )


@bot.message_handler(state=BudgetSearchStates.input_city)
def budget_input_city_state(message: Message) -> None:
    HandleMsg.input_city(message.chat.id, message.from_user.id,
                         message.text, low_price_shortcut)


@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_callback(call: CallbackQuery):
    HandleMsg.confirm_city(call.message.chat.id, call.from_user.id, call.data)


@bot.message_handler(state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_msg(message: Message) -> None:
    HandleMsg.confirm_city(message.chat.id, message.from_user.id)


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
    check_in_date = extract_date(call)
    reply_text = "Select check out date:"
    correct_date = True
    if not check_in_date:
        reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
        correct_date = False
    budget_reply_msg_check_in_date(call.from_user.id, call.message.chat.id,
                                   correct_date, reply_text, check_in_date)


@bot.message_handler(state=BudgetSearchStates.check_in_date)
def budget_check_in_date_state_msg(message: Message) -> None:
    reply_text = "Select check out date:"
    correct_date = False
    check_in_date = ''
    exception_message = check_date_format(message.text)
    if exception_message:
        reply_text = "{exception_message}\n Use calendar!".format(
            exception_message=exception_message)
    else:
        check_in_date = convert_str_date_to_dict(message.text)
        correct_date = True
    budget_reply_msg_check_in_date(message.from_user.id, message.chat.id,
                                   correct_date, reply_text, check_in_date)


def budget_reply_msg_check_in_date(user_id: int, chat_id: int,
                                   correct_date: bool, reply_text: str,
                                   check_in_date: dict) -> None:
    now = date.today()
    if correct_date is True and not valid_check_in_date(check_in_date):
        reply_text = "Select check in date starting {current_date}".format(
            current_date=date.today().strftime('%d %b %Y')
        )
    elif correct_date:
        bot.set_state(user_id=user_id,
                      state=BudgetSearchStates.check_out_date,
                      chat_id=chat_id
                      )
        StateData.save_state_data_by_key(chat_id=chat_id,
                               user_id=user_id,
                               key="checkInDate",
                               value=check_in_date)
    bot.send_message(chat_id, reply_text,
                     reply_markup=generate_calendar_days(year=now.year,
                                                         month=now.month))


@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_cb(call: CallbackQuery) -> None:
    check_out_date = extract_date(call)
    reply_text = "Type number of travellers (max 14): "
    correct_date = True
    if not check_out_date:
        reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
        correct_date = False
    budget_reply_msg_check_out_date(call.from_user.id, call.message.chat.id,
                                    correct_date, reply_text, check_out_date)


@bot.message_handler(state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_msg(message: Message) -> None:
    reply_text = "Type number of travellers (max 14): "
    correct_date = False
    check_out_date = ''
    exception_message = check_date_format(message.text)
    if exception_message:
        reply_text = "{exception_message}\n Use calendar!".format(
            exception_message=exception_message)
    else:
        check_out_date = convert_str_date_to_dict(message.text)
        correct_date = True
    budget_reply_msg_check_out_date(message.from_user.id, message.chat.id,
                                    correct_date, reply_text, check_out_date)


def budget_reply_msg_check_out_date(user_id: int, chat_id: int, correct_date: bool,
                                    reply_text: str, check_out_date: dict) -> None:
    now = date.today()
    reply_markup = generate_calendar_days(year=now.year,
                                          month=now.month)
    check_in_date = StateData.retrieve_data_by_key(chat_id, user_id, 'checkInDate')
    if (correct_date is True and
            not valid_check_out_date(check_in_date, check_out_date)):
        reply_text = ("Select check out date after check in date"
                      " {day}.{month}.{year}").format(
            day=check_in_date["day"],
            month=check_in_date["month"],
            year=check_in_date["year"]
        )
    elif correct_date:
        bot.set_state(user_id=user_id,
                      state=BudgetSearchStates.travellers,
                      chat_id=chat_id
                      )
        StateData.save_state_data_by_key(chat_id=chat_id,
                               user_id=user_id,
                               key="checkOutDate",
                               value=check_out_date)
        reply_markup = cancel_reply_keyboard
    bot.send_message(chat_id, reply_text,
                     reply_markup=reply_markup)


@bot.message_handler(state=BudgetSearchStates.travellers)
def budget_travellers_state(message: Message) -> None:
    reply_text = "How many hotels to display (max 10)?"
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = "Use digits to set number of travellers!\n(ex. 2)"
    elif int(received_text) >= 15:
        reply_text = "Max number of travellers is 14!\n(ex. 5)"
    elif int(received_text) <= 0:
        reply_text = "Min number of travellers is 1!\n(ex. 1)"
    else:
        bot.set_state(user_id=message.from_user.id,
                      state=BudgetSearchStates.hotels_amount,
                      chat_id=message.chat.id
                      )
        StateData.save_state_data_by_key(chat_id=message.chat.id,
                               user_id=message.from_user.id,
                               key="adults",
                               value=int(received_text))
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=cancel_reply_keyboard
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_amount)
def budget_hotel_amount_state(message: Message) -> None:
    reply_text = "Do you need photo of hotels?\nType 'yes' or 'no'."
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = 'Use digits to set hotels amount!\n(ex. 3)'
    elif int(received_text) >= 11:
        reply_text = "Max number of hotels to display is 10!\n(ex. 10)"
    elif int(received_text) <= 0:
        reply_text = "Min number of hotels to display is 1!\n(ex. 1)"
    else:
        bot.set_state(user_id=message.from_user.id,
                      state=BudgetSearchStates.hotels_photo,
                      chat_id=message.chat.id
                      )
        StateData.save_state_data_by_key(chat_id=message.chat.id,
                               user_id=message.from_user.id,
                               key="hotels_amount",
                               value=int(received_text)
                               )
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=cancel_reply_keyboard
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_photo)
def budget_photo_state(message: Message) -> None:
    reply_text = "How many photos to display (max 5)?"
    reply_markup = cancel_reply_keyboard
    received_text = message.text.strip().lower()
    if not received_text.isalpha():
        reply_text = "Use letters only!\n(ex. yes)"
    elif received_text not in ['yes', 'no']:
        reply_text = "Type 'yes' or 'no'.\n(ex. yes)"
    else:
        StateData.save_state_data_by_key(chat_id=message.chat.id,
                               user_id=message.from_user.id,
                               key="display_hotel_photos",
                               value=received_text)
        if received_text == "yes":
            bot.set_state(user_id=message.from_user.id,
                          state=BudgetSearchStates.hotels_photo_amount,
                          chat_id=message.chat.id
                          )
        else:
            StateData.save_state_data_by_key(chat_id=message.chat.id,
                                   user_id=message.from_user.id,
                                   key="hotel_photo_amount",
                                   value=0)
            send_final_response(message.chat.id, message.from_user.id)
            return None
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=reply_markup
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_photo_amount)
def budget_photo_amount_state(message: Message) \
        -> None:
    reply_markup = cancel_reply_keyboard
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = "Use digits to set photos amount!\n(ex. 3)"
    elif int(received_text) > 5:
        reply_text = "Max number of photos to display is 5.\n(ex. 5)"
    elif int(received_text) <= 0:
        reply_text = "Min number of photos to display is 1.\n(ex. 1)"
    else:
        StateData.save_state_data_by_key(chat_id=message.chat.id,
                               user_id=message.from_user.id,
                               key="hotel_photo_amount",
                               value=int(received_text))
        send_final_response(message.chat.id, message.from_user.id)
        return None
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=reply_markup
                     )
