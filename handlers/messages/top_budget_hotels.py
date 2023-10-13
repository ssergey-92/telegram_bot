from typing import Union, Callable
from datetime import date
from telebot.types import Message, CallbackQuery

from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from keyboards.reply_keyboard.cancel import cancel_reply_keyboard
from database.history_model import History, db
from database.CRUD_interface import CrudDb
from loader import bot
from states.BudgetSearch import BudgetSearchStates
from config_data.config import BOT_COMMANDS
from .utils.state_data import save_state_data, take_state_data, delete_state
from .utils.date_handling import (extract_date, valid_check_in_date,
                                  check_date_format, valid_check_out_date,
                                  convert_str_date_to_dict)
from .utils.user_input_data_check import eng_language_check

@bot.message_handler(commands=[BOT_COMMANDS[3][0]])  # low_price cmd
def low_price_command(message: Message) -> None:
    reply_msg_low_price(message.chat.id, message.from_user.id)


def reply_msg_low_price(chat_id: int, user_id: int) -> None:
    reply_text = 'Type city name:'
    command = ''.join(BOT_COMMANDS[3][1])
    CrudDb.create_entries(db, History, user_id, command)
    delete_state(chat_id, user_id)
    bot.set_state(user_id, BudgetSearchStates.input_city, chat_id)
    bot.send_message(chat_id, reply_text,
                     reply_markup=cancel_reply_keyboard)


@bot.message_handler(state=BudgetSearchStates.input_city)
def budget_input_city_state(message: Message) -> None:
    received_text = message.text.strip().lower()
    reply_markup = cancel_reply_keyboard
    reply_text = "You mean:"
    if not received_text.isalpha():
        reply_text = 'Enter a city name using letters only!\n(ex. Miami)'
    elif not eng_language_check(received_text):
        reply_text = 'Enter a city name using ENGLISH letters only!\n(ex. Miami)'
    else:
        bot.set_state(user_id=message.from_user.id,
                      state=BudgetSearchStates.confirm_city,
                      chat_id=message.chat.id
                      )
        save_state_data(chart_id=message.chat.id,
                        user_id=message.from_user.id,
                        title='Input city',
                        definition=message.text)
        #api                                                                      ###################
        reply_markup = cities
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=reply_markup)


#################################################
@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_cb(call: CallbackQuery):

    pass


@bot.message_handler(state=BudgetSearchStates.confirm_city)
def budget_confirm_city_state_msg(message: Message) -> None:


    received_text = message.text.strip()
    if not received_text.isalpha():
        reply_text = 'Enter a city name using letters only!\n(ex. Miami)',
    # elif received_text not in []:
    # hotels request
    # check if city is in hotels data
    else:
        pass


def budget_reply_msg_confirm_city(user_id: int, chat_id: int,
                                   correct_date: bool,  reply_text: str,
                                   city_data: dict) -> None:
    reply_text = 'Select check in date:'
    bot.set_state(user_id=user_id,
                  state=BudgetSearchStates.check_in_date,
                  chat_id=chat_id
                  )
    save_state_data(chart_id=chat_id,
                    user_id=user_id,
                    title='Confirmed city',
                    definition=city_data)
    now = date.today()
    bot.send_message(chat_id, reply_text,
                     reply_markup=generate_calendar_days(year=now.year,
                                                         month=now.month))


#################################################
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
                                   correct_date: bool,  reply_text: str,
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
        save_state_data(chart_id=chat_id,
                        user_id=user_id,
                        title='checkInDate:',
                        definition=check_in_date)
    bot.send_message(chat_id, reply_text,
                     reply_markup=generate_calendar_days(year=now.year,
                                                         month=now.month))


@bot.callback_query_handler(func=lambda call: call,
                            state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_cb(call: CallbackQuery) -> None:
    check_out_date = extract_date(call)
    reply_text = "Type number of travellers: "
    correct_date = True
    if not check_out_date:
        reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
        correct_date = False
    budget_reply_msg_check_out_date(call.from_user.id, call.message.chat.id,
                                    correct_date, reply_text, check_out_date)


@bot.message_handler(state=BudgetSearchStates.check_out_date)
def budget_check_out_date_state_msg(message: Message) -> None:
    reply_text = "Type number of travellers: "
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
    check_in_date = take_state_data(chat_id, user_id, 'checkInDate:')
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
        save_state_data(chart_id=chat_id,
                        user_id=user_id,
                        title='checkOutDate',
                        definition=check_out_date)
        reply_markup = cancel_reply_keyboard
    bot.send_message(chat_id, reply_text,
                     reply_markup=reply_markup)


@bot.message_handler(state=BudgetSearchStates.travellers)
def budget_travellers_state(message: Message) -> None:
    reply_text = "How many hotels to display?"
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = 'Use digits to set number of travellers!\n(ex. 2)'
    else:
        bot.set_state(user_id=message.from_user.id,
                      state=BudgetSearchStates.hotels_amount,
                      chat_id=message.chat.id
                      )
        save_state_data(chart_id=message.chat.id,
                        user_id=message.from_user.id,
                        title='Travellers',
                        definition=received_text)
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=cancel_reply_keyboard
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_amount)
def budget_amount_state(message: Message) -> None:
    reply_text = "Do you need photo of hotels?\nType 'yes' or 'no'."
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = 'Use digits to set hotels amount!\n(ex. 10)'
    else:
        bot.set_state(user_id=message.from_user.id,
                      state=BudgetSearchStates.hotels_photo,
                      chat_id=message.chat.id
                      )
        save_state_data(chart_id=message.chat.id,
                        user_id=message.from_user.id,
                        title='Hotels amount',
                        definition=received_text)
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=cancel_reply_keyboard
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_photo)
def budget_photo_state(message: Message) -> Union[None, Callable]:
    reply_text = "How many photos to display?"
    received_text = message.text.strip().lower()
    if not received_text.isalpha():
        reply_text = "Use letters only!\n(ex. yes)"
    elif received_text not in ['yes', 'no']:
        reply_text = "Type 'yes' or 'no'.\n(ex. yes)"
    else:
        save_state_data(chart_id=message.chat.id,
                        user_id=message.from_user.id,
                        title='Display photos of hotel',
                        definition=received_text)
        if received_text == 'yes':
            bot.set_state(user_id=message.from_user.id,
                          state=BudgetSearchStates.hotels_photo_amount,
                          chat_id=message.chat.id
                          )
        else:
            return update_user_request_history(message.chat.id, message.from_user.id)
    bot.send_message(message.chat.id, reply_text,
                     reply_markup=cancel_reply_keyboard
                     )


@bot.message_handler(state=BudgetSearchStates.hotels_photo_amount)
def budget_photo_amount_state(message: Message) \
        -> Union[None, Callable]:
    received_text = message.text.strip()
    if not received_text.isdigit():
        reply_text = "Use digits to set photos amount!\n(ex. 3)"
        bot.send_message(message.chat.id, reply_text,
                         reply_markup=cancel_reply_keyboard
                         )
    else:
        save_state_data(chart_id=message.chat.id,
                        user_id=message.from_user.id,
                        title='Photos of hotel',
                        definition=received_text)
        return update_user_request_history(message.chat.id, message.from_user.id)


def update_user_request_history(chart_id: int, user_id: int) -> None:
    request_info = get_info_from_state_data(chart_id, user_id)
    CrudDb.update_last_user_entry(db, History, user_id, History.user_request,
                                  request_info)
    delete_state(chart_id, user_id)


def get_info_from_state_data(chart_id: int, user_id: int) -> dict:
    with bot.retrieve_data(user_id, chart_id) as data:
        user_request_info = data
    return user_request_info

# @bot.message_handler(state=MyStates.age, is_digit=True)
# def ready_for_answer(message):
#     """
#     State 3. Will process when user's state is MyStates.age.
#     """
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#         msg = ("Ready, take a look:\n<b>"
#                f"Name: {data['name']}\n"
#                f"Surname: {data['surname']}\n"
#                f"Age: {message.text}</b>")
#         bot.send_message(message.chat.id, msg, parse_mode="html")
#     bot.delete_state(message.from_user.id, message.chat.id)
