from telebot.types import Message, CallbackQuery
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from loader import bot
from states.custom_search import CustomSearchStates
from config_data.config import BOT_COMMANDS
from .handle_state_messages import HandleMsg

best_deal_cmd = BOT_COMMANDS[5][0]
best_deal_shortcut = BOT_COMMANDS[5][1]


@bot.message_handler(commands=[best_deal_cmd])
def best_deal_price_command(message: Message) -> None:
    reply_msg_best_deal(message.chat.id, message.from_user.id)


def reply_msg_best_deal(chat_id: int, user_id: int) -> None:
    HandleMsg.initialize_command(chat_id, user_id, best_deal_shortcut,
                                 "DISTANCE",
                                 0, 0,
                                 CustomSearchStates.input_city)


@bot.message_handler(state=CustomSearchStates.input_city)
def best_deal_input_city_state(message: Message) -> None:
    HandleMsg.input_city(message.chat.id, message.from_user.id,
                         message.text, best_deal_shortcut,
                         CustomSearchStates.confirm_city)


@bot.callback_query_handler(func=lambda call: call,
                            state=CustomSearchStates.confirm_city)
def best_deal_confirm_city_state_callback(call: CallbackQuery):
    reply_text = ("Type minimum hotel price in USD per day:\n"
                  "*USD - United States dollar.")
    HandleMsg.confirm_city(call.message.chat.id, call.from_user.id,
                           CustomSearchStates.min_price,
                           CustomSearchStates.input_city, reply_text, call.data)


@bot.message_handler(state=CustomSearchStates.confirm_city)
def best_deal_confirm_city_state_msg(message: Message) -> None:
    HandleMsg.confirm_city(message.chat.id, message.from_user.id,
                           CustomSearchStates.min_price,
                           CustomSearchStates.input_city)


@bot.message_handler(state=CustomSearchStates.min_price)
def best_deal_min_price_state(message: Message) -> None:
    HandleMsg.set_min_price(message.chat.id, message.from_user.id,
                            message.text, CustomSearchStates.max_price)


@bot.message_handler(state=CustomSearchStates.max_price)
def best_deal_max_price_state(message: Message) -> None:
    HandleMsg.set_max_price(message.chat.id, message.from_user.id,
                            message.text, CustomSearchStates.min_distance)


@bot.message_handler(state=CustomSearchStates.min_distance)
def best_deal_min_distance_state(message: Message) -> None:
    HandleMsg.set_min_distance(message.chat.id, message.from_user.id,
                               message.text, CustomSearchStates.max_distance)


@bot.message_handler(state=CustomSearchStates.max_distance)
def best_deal_max_distance_state(message: Message) -> None:
    HandleMsg.set_max_distance(message.chat.id, message.from_user.id,
                               message.text, CustomSearchStates.check_in_date)


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
                            state=CustomSearchStates.check_in_date)
def best_deal_check_in_date_state_cb(call: CallbackQuery) -> None:
    check_in_date = HandleMsg.check_calendar_callback(call)
    if check_in_date:
        HandleMsg.check_in(call.message.chat.id, call.from_user.id,
                           check_in_date, CustomSearchStates.check_out_date)


@bot.message_handler(state=CustomSearchStates.check_in_date)
def best_deal_check_in_date_state_msg(message: Message) -> None:
    check_in_date = HandleMsg.check_calendar_message(message)
    if check_in_date:
        HandleMsg.check_in(message.chat.id, message.from_user.id,
                           check_in_date, CustomSearchStates.check_out_date)


@bot.callback_query_handler(func=lambda call: call,
                            state=CustomSearchStates.check_out_date)
def best_deal_check_out_date_state_cb(call: CallbackQuery) -> None:
    check_out_date = HandleMsg.check_calendar_callback(call)
    if check_out_date:
        HandleMsg.check_out(call.message.chat.id, call.from_user.id,
                            check_out_date, CustomSearchStates.travellers)


@bot.message_handler(state=CustomSearchStates.check_out_date)
def best_deal_check_out_date_state_msg(message: Message) -> None:
    check_out_date = HandleMsg.check_calendar_message(message)
    if check_out_date:
        HandleMsg.check_out(message.chat.id, message.from_user.id,
                            check_out_date, CustomSearchStates.travellers)


@bot.message_handler(state=CustomSearchStates.travellers)
def best_deal_travellers_state(message: Message) -> None:
    HandleMsg.set_travellers(message.chat.id, message.from_user.id,
                             message.text, CustomSearchStates.hotels_amount)


@bot.message_handler(state=CustomSearchStates.hotels_amount)
def best_deal_hotel_amount_state(message: Message) -> None:
    HandleMsg.set_hotel_amount(message.chat.id, message.from_user.id,
                               message.text, CustomSearchStates.hotels_photo)


@bot.message_handler(state=CustomSearchStates.hotels_photo)
def best_deal_photo_state(message: Message) -> None:
    HandleMsg.show_hotel_photo(message.chat.id, message.from_user.id,
                               message.text, CustomSearchStates.hotels_photo_amount)


@bot.message_handler(state=CustomSearchStates.hotels_photo_amount)
def best_deal_photo_amount_state(message: Message) -> None:
    HandleMsg.set_photos_amount(message.chat.id, message.from_user.id,
                                message.text)
