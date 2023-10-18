# from typing import Union, Callable
# from datetime import date
# from telebot.types import (Message, CallbackQuery, InlineKeyboardMarkup)
#
# from keyboards.inline_keyboard.calender.keyboards import (
#     generate_calendar_days, generate_calendar_months)
# from keyboards.inline_keyboard.calender.filters import (calendar_factory,
#                                                         calendar_zoom)
# from keyboards.inline_keyboard.search_cities import (
#     create_search_city_inline_keyboard)
# from keyboards.reply_keyboard.cancel import cancel_reply_keyboard
# from database.history_model import History, db
# from database.CRUD_interface import CrudDb
# from loader import bot
# from states.BudgetSearch import BudgetSearchStates
# from config_data.config import BOT_COMMANDS
# from .utils.state_data import StateData
# from .utils.date_handling import (extract_date, valid_check_in_date,
#                                   check_date_format, valid_check_out_date,
#                                   convert_str_date_to_dict)
# from .utils.user_input_data_check import eng_language_check
# from .utils.response_for_user import send_final_response
# from handlers.sites_API.rapidapi_hotels import HotelsApi
#
#
# @bot.message_handler(commands=[BOT_COMMANDS[3][0]])  # low_price cmd
# def low_price_command(message: Message) -> None:
#     reply_msg_low_price(message.chat.id, message.from_user.id)
#
#
# def reply_msg_low_price(chat_id: int, user_id: int) -> None:
#     reply_text = 'Type city name:'
#     command = ''.join(BOT_COMMANDS[3][1])
#     CrudDb.create_entries(db, History, user_id, command)
#     StateData.delete_state(chat_id, user_id)
#     bot.set_state(user_id, BudgetSearchStates.input_city, chat_id)
#     with bot.retrieve_data(user_id, chat_id) as data:
#         data["command"] = command
#         data["min_price"] = 1
#         data["max_price"] = 1000000
#         data["sort"] = "PRICE_LOW_TO_HIGH"
#     bot.send_message(chat_id, reply_text,
#                      reply_markup=cancel_reply_keyboard)
#
#
# @bot.message_handler(state=BudgetSearchStates.input_city)
# def budget_input_city_state(message: Message) -> None:
#     received_text = message.text.strip(',. ').replace(',', '').lower()
#     reply_markup = cancel_reply_keyboard
#     reply_text = "You mean:"
#     for i_word in received_text.split(' '):
#         if not i_word.isalpha():
#             reply_text = "Enter a city name using letters only!\n(ex. Miami)"
#         elif not eng_language_check(i_word):
#             reply_text = "Enter a city name using ENGLISH letters only!\n(ex. Miami)"
#         else:
#             cities_data = HotelsApi.check_city(message.from_user.id,
#                                                received_text, BOT_COMMANDS[3][0])
#             if cities_data:
#                 bot.set_state(user_id=message.from_user.id,
#                               state=BudgetSearchStates.confirm_city,
#                               chat_id=message.chat.id
#                               )
#                 StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                        user_id=message.from_user.id,
#                                        key="Input city",
#                                        value=message.text)
#                 StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                        user_id=message.from_user.id,
#                                        key="searched_city_result",
#                                        value=cities_data)
#                 reply_markup = create_search_city_inline_keyboard(cities_data)
#             else:
#                 reply_text = ("Sorry, there is no city '{input_city}' in our database.\n"
#                               "Try to enter proper city name or use another place.".format(
#                     input_city=message.text
#                 )
#                 )
#     bot.send_message(message.chat.id, reply_text, reply_markup=reply_markup)
#
#
# @bot.callback_query_handler(func=lambda call: call,
#                             state=BudgetSearchStates.confirm_city)
# def budget_confirm_city_state_cb(call: CallbackQuery):
#     is_confirmed = False
#     reply_text = "'Type city name: "
#     reply_markup = None
#     confirmed_city = None
#     if not call.data.isdigit():
#         bot.set_state(user_id=call.from_user.id,
#                       state=BudgetSearchStates.input_city,
#                       chat_id=call.message.chat.id
#                       )
#     else:
#         searched_city_result = StateData.retrieve_data_by_key(call.message.chat.id,
#                                                               call.from_user.id, 'searched_city_result')
#         confirmed_city = searched_city_result[int(call.data)]
#         is_confirmed = True
#         reply_text = "Select check in date:"
#     budget_reply_msg_confirm_city(call.from_user.id, call.message.chat.id,
#                                   reply_text, reply_markup, is_confirmed, confirmed_city)
#
#
# @bot.message_handler(state=BudgetSearchStates.confirm_city)
# def budget_confirm_city_state_msg(message: Message) -> None:
#     searched_city_result = StateData.retrieve_data_by_key(message.chat.id,
#                                                           message.from_user.id, 'searched_city_result')
#     reply_markup = create_search_city_inline_keyboard(searched_city_result)
#     reply_text = "Kindly select one of the below options!"
#     budget_reply_msg_confirm_city(message.from_user.id, message.chat.id,
#                                   reply_text, reply_markup)
#
#
# def budget_reply_msg_confirm_city(user_id: int, chat_id: int, reply_text: str,
#                                   reply_markup: InlineKeyboardMarkup = None,
#                                   is_confirmed: bool = False, confirmed_city: dict = None) \
#         -> None:
#     if is_confirmed:
#         bot.set_state(user_id=user_id,
#                       state=BudgetSearchStates.check_in_date,
#                       chat_id=chat_id
#                       )
#         StateData.save_state_data_by_key(chat_id=chat_id,
#                                user_id=user_id,
#                                key='regionId',
#                                value=confirmed_city['regionId'])
#         StateData.save_state_data_by_key(chat_id=chat_id,
#                                user_id=user_id,
#                                key='fullName',
#                                value=confirmed_city['fullName'])
#         now = date.today()
#         reply_markup = generate_calendar_days(year=now.year,
#                                               month=now.month)
#
#     bot.send_message(chat_id, reply_text,
#                      reply_markup=reply_markup)
#
#
# @bot.callback_query_handler(func=None,
#                             calendar_config=calendar_factory.filter())
# def calendar_action_handler(call: CallbackQuery) -> None:
#     callback_data: dict = calendar_factory.parse(callback_data=call.data)
#     year, month = int(callback_data['year']), int(callback_data['month'])
#
#     bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
#                                   reply_markup=generate_calendar_days(year=year,
#                                                                       month=month))
#
#
# @bot.callback_query_handler(func=None,
#                             calendar_zoom_config=calendar_zoom.filter())
# def calendar_zoom_out_handler(call: CallbackQuery) -> None:
#     callback_data: dict = calendar_zoom.parse(callback_data=call.data)
#     year = int(callback_data.get('year'))
#
#     bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
#                                   reply_markup=generate_calendar_months(year=year))
#
#
# @bot.callback_query_handler(func=lambda call: call,
#                             state=BudgetSearchStates.check_in_date)
# def budget_check_in_date_state_cb(call: CallbackQuery) -> None:
#     check_in_date = extract_date(call)
#     reply_text = "Select check out date:"
#     correct_date = True
#     if not check_in_date:
#         reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
#         correct_date = False
#     budget_reply_msg_check_in_date(call.from_user.id, call.message.chat.id,
#                                    correct_date, reply_text, check_in_date)
#
#
# @bot.message_handler(state=BudgetSearchStates.check_in_date)
# def budget_check_in_date_state_msg(message: Message) -> None:
#     reply_text = "Select check out date:"
#     correct_date = False
#     check_in_date = ''
#     exception_message = check_date_format(message.text)
#     if exception_message:
#         reply_text = "{exception_message}\n Use calendar!".format(
#             exception_message=exception_message)
#     else:
#         check_in_date = convert_str_date_to_dict(message.text)
#         correct_date = True
#     budget_reply_msg_check_in_date(message.from_user.id, message.chat.id,
#                                    correct_date, reply_text, check_in_date)
#
#
# def budget_reply_msg_check_in_date(user_id: int, chat_id: int,
#                                    correct_date: bool, reply_text: str,
#                                    check_in_date: dict) -> None:
#     now = date.today()
#     if correct_date is True and not valid_check_in_date(check_in_date):
#         reply_text = "Select check in date starting {current_date}".format(
#             current_date=date.today().strftime('%d %b %Y')
#         )
#     elif correct_date:
#         bot.set_state(user_id=user_id,
#                       state=BudgetSearchStates.check_out_date,
#                       chat_id=chat_id
#                       )
#         StateData.save_state_data_by_key(chat_id=chat_id,
#                                user_id=user_id,
#                                key="checkInDate",
#                                value=check_in_date)
#     bot.send_message(chat_id, reply_text,
#                      reply_markup=generate_calendar_days(year=now.year,
#                                                          month=now.month))
#
#
# @bot.callback_query_handler(func=lambda call: call,
#                             state=BudgetSearchStates.check_out_date)
# def budget_check_out_date_state_cb(call: CallbackQuery) -> None:
#     check_out_date = extract_date(call)
#     reply_text = "Type number of travellers (max 14): "
#     correct_date = True
#     if not check_out_date:
#         reply_text = "Press digit on calendar!\n(ex. 1, 2.. 31)"
#         correct_date = False
#     budget_reply_msg_check_out_date(call.from_user.id, call.message.chat.id,
#                                     correct_date, reply_text, check_out_date)
#
#
# @bot.message_handler(state=BudgetSearchStates.check_out_date)
# def budget_check_out_date_state_msg(message: Message) -> None:
#     reply_text = "Type number of travellers (max 14): "
#     correct_date = False
#     check_out_date = ''
#     exception_message = check_date_format(message.text)
#     if exception_message:
#         reply_text = "{exception_message}\n Use calendar!".format(
#             exception_message=exception_message)
#     else:
#         check_out_date = convert_str_date_to_dict(message.text)
#         correct_date = True
#     budget_reply_msg_check_out_date(message.from_user.id, message.chat.id,
#                                     correct_date, reply_text, check_out_date)
#
#
# def budget_reply_msg_check_out_date(user_id: int, chat_id: int, correct_date: bool,
#                                     reply_text: str, check_out_date: dict) -> None:
#     now = date.today()
#     reply_markup = generate_calendar_days(year=now.year,
#                                           month=now.month)
#     check_in_date = StateData.retrieve_data_by_key(chat_id, user_id, 'checkInDate')
#     if (correct_date is True and
#             not valid_check_out_date(check_in_date, check_out_date)):
#         reply_text = ("Select check out date after check in date"
#                       " {day}.{month}.{year}").format(
#             day=check_in_date["day"],
#             month=check_in_date["month"],
#             year=check_in_date["year"]
#         )
#     elif correct_date:
#         bot.set_state(user_id=user_id,
#                       state=BudgetSearchStates.travellers,
#                       chat_id=chat_id
#                       )
#         StateData.save_state_data_by_key(chat_id=chat_id,
#                                user_id=user_id,
#                                key="checkOutDate",
#                                value=check_out_date)
#         reply_markup = cancel_reply_keyboard
#     bot.send_message(chat_id, reply_text,
#                      reply_markup=reply_markup)
#
#
# @bot.message_handler(state=BudgetSearchStates.travellers)
# def budget_travellers_state(message: Message) -> None:
#     reply_text = "How many hotels to display (max 10)?"
#     received_text = message.text.strip()
#     if not received_text.isdigit():
#         reply_text = "Use digits to set number of travellers!\n(ex. 2)"
#     elif int(received_text) >= 15:
#         reply_text = "Max number of travellers is 14!\n(ex. 5)"
#     elif int(received_text) <= 0:
#         reply_text = "Min number of travellers is 1!\n(ex. 1)"
#     else:
#         bot.set_state(user_id=message.from_user.id,
#                       state=BudgetSearchStates.hotels_amount,
#                       chat_id=message.chat.id
#                       )
#         StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                user_id=message.from_user.id,
#                                key="adults",
#                                value=int(received_text))
#     bot.send_message(message.chat.id, reply_text,
#                      reply_markup=cancel_reply_keyboard
#                      )
#
#
# @bot.message_handler(state=BudgetSearchStates.hotels_amount)
# def budget_hotel_amount_state(message: Message) -> None:
#     reply_text = "Do you need photo of hotels?\nType 'yes' or 'no'."
#     received_text = message.text.strip()
#     if not received_text.isdigit():
#         reply_text = 'Use digits to set hotels amount!\n(ex. 3)'
#     elif int(received_text) >= 11:
#         reply_text = "Max number of hotels to display is 10!\n(ex. 10)"
#     elif int(received_text) <= 0:
#         reply_text = "Min number of hotels to display is 1!\n(ex. 1)"
#     else:
#         bot.set_state(user_id=message.from_user.id,
#                       state=BudgetSearchStates.hotels_photo,
#                       chat_id=message.chat.id
#                       )
#         StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                user_id=message.from_user.id,
#                                key="hotels_amount",
#                                value=int(received_text)
#                                )
#     bot.send_message(message.chat.id, reply_text,
#                      reply_markup=cancel_reply_keyboard
#                      )
#
#
# @bot.message_handler(state=BudgetSearchStates.hotels_photo)
# def budget_photo_state(message: Message) -> None:
#     reply_text = "How many photos to display (max 5)?"
#     reply_markup = cancel_reply_keyboard
#     received_text = message.text.strip().lower()
#     if not received_text.isalpha():
#         reply_text = "Use letters only!\n(ex. yes)"
#     elif received_text not in ['yes', 'no']:
#         reply_text = "Type 'yes' or 'no'.\n(ex. yes)"
#     else:
#         StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                user_id=message.from_user.id,
#                                key="display_hotel_photos",
#                                value=received_text)
#         if received_text == "yes":
#             bot.set_state(user_id=message.from_user.id,
#                           state=BudgetSearchStates.hotels_photo_amount,
#                           chat_id=message.chat.id
#                           )
#         else:
#             StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                    user_id=message.from_user.id,
#                                    key="hotel_photo_amount",
#                                    value=0)
#             send_final_response(message.chat.id, message.from_user.id)
#             return None
#     bot.send_message(message.chat.id, reply_text,
#                      reply_markup=reply_markup
#                      )
#
#
# @bot.message_handler(state=BudgetSearchStates.hotels_photo_amount)
# def budget_photo_amount_state(message: Message) \
#         -> None:
#     reply_markup = cancel_reply_keyboard
#     received_text = message.text.strip()
#     if not received_text.isdigit():
#         reply_text = "Use digits to set photos amount!\n(ex. 3)"
#     elif int(received_text) > 5:
#         reply_text = "Max number of photos to display is 5.\n(ex. 5)"
#     elif int(received_text) <= 0:
#         reply_text = "Min number of photos to display is 1.\n(ex. 1)"
#     else:
#         StateData.save_state_data_by_key(chat_id=message.chat.id,
#                                user_id=message.from_user.id,
#                                key="hotel_photo_amount",
#                                value=int(received_text))
#         send_final_response(message.chat.id, message.from_user.id)
#         return None
#     bot.send_message(message.chat.id, reply_text,
#                      reply_markup=reply_markup
#                      )
