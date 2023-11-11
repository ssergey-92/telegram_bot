from datetime import date

from telebot.types import Message, CallbackQuery
from keyboards.inline_keyboard.calender.keyboards import (
    generate_calendar_days, generate_calendar_months)
from keyboards.inline_keyboard.calender.filters import (calendar_factory,
                                                        calendar_zoom)
from loader import bot
from states.luxury_search import LuxurySearchStates
from config_data.config import BOT_COMMANDS
from .utils.search_state_messages import HandleSearchMsg

high_price_cmd = BOT_COMMANDS[4][0]
high_price_shortcut = BOT_COMMANDS[4][1]


@bot.message_handler(commands=[high_price_cmd])
def high_price_command(message: Message) -> None:
    """
    Catching unstated incoming user reply message which contains bot
    command "high_price" and calling function(reply_msg_high_price()) for
    handling command.

    :param message: user reply data
    :type message: Message
    """

    reply_msg_high_price(message.chat.id, message.from_user.id)


def reply_msg_high_price(chat_id: int, user_id: int) -> None:
    """
    Intermediate function for calling HandleSearchMsg.initialize_command() due
    to different types of user reply formats (Message, Callback)

    :param chat_id: Chat identifier
    :type chat_id: int
    :param user_id: User identifier
    :type user_id: int
    """

    HandleSearchMsg.initialize_command(chat_id, user_id, high_price_shortcut,
                                       "PRICE_LOW_TO_HIGH",
                                       1, 1000000,
                                       LuxurySearchStates.input_city)


@bot.message_handler(state=LuxurySearchStates.input_city)
def luxury_input_city_state(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.input_city and calling
    HandleSearchMsg.input_city() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.input_city(message.chat.id, message.from_user.id,
                               message.text, high_price_shortcut,
                               LuxurySearchStates.confirm_city)


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.confirm_city)
def luxury_confirm_city_state_callback(call: CallbackQuery):
    """
    Catching state: LuxurySearchStates.confirm_city with callback query from
    a callback button in search_cities inline keyboard and calling
    HandleSearchMsg.confirm_city() for handling it.

    :param call: user reply data
    :type call: CallbackQuery
    """

    reply_text = "Select check in date:"
    now = date.today()
    reply_markup = generate_calendar_days(year=now.year,
                                          month=now.month)
    HandleSearchMsg.confirm_city(call.message.chat.id, call.from_user.id,
                                 LuxurySearchStates.check_in_date,
                                 LuxurySearchStates.input_city, reply_text, call.data,
                                 reply_markup)


@bot.message_handler(state=LuxurySearchStates.confirm_city)
def luxury_confirm_city_state_msg(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.confirm_city and calling
    HandleSearchMsg.confirm_city() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.confirm_city(message.chat.id, message.from_user.id,
                                 LuxurySearchStates.check_in_date,
                                 LuxurySearchStates.input_city)


@bot.callback_query_handler(func=None,
                            calendar_config=calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery) -> None:
    """
    Catching callback query with calendar_config  from callback button
    "Previous month" or "Next month" from calendar inline keyboard  and
    recreating calendar for selected month.

    :param call: user reply data
    :type call: CallbackQuery
    """

    callback_data: dict = calendar_factory.parse(callback_data=call.data)
    year, month = int(callback_data['year']), int(callback_data['month'])

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_days(year=year,
                                                                      month=month))


@bot.callback_query_handler(func=None,
                            calendar_zoom_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery) -> None:
    """
    Catching callback query with calendar_zoom_config  from callback button
    "Zoom out", "previous year", "next year" from calendar inline keyboard
    and creating calendar for selected year(default current year).

    :param call: user reply data
    :type call: CallbackQuery
    """

    callback_data: dict = calendar_zoom.parse(callback_data=call.data)
    year = int(callback_data.get('year'))

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_months(year=year))


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.check_in_date)
def luxury_check_in_date_state_cb(call: CallbackQuery) -> None:
    """
    Catching state: LuxurySearchStates.check_in_date with callback query from
    a callback button (except "Zoom out", "previous year", "next year",
    "Previous month" or "Next month")  in calendar inline keyboard and calling
    HandleSearchMsg.check_in() for handling it if there is check in date.

    :param call: user reply data
    :type call: CallbackQuery
    """

    check_in_date = HandleSearchMsg.check_calendar_callback(call)
    if check_in_date:
        HandleSearchMsg.check_in(call.message.chat.id, call.from_user.id,
                                 check_in_date, LuxurySearchStates.check_out_date)


@bot.message_handler(state=LuxurySearchStates.check_in_date)
def luxury_check_in_date_state_msg(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.check_in_date and calling
    HandleSearchMsg.check_in() for handling it if check in date passed check in
    HandleSearchMsg.check_calendar_date().

    :param message: user reply data
    :type message: Message
    """

    check_in_date = HandleSearchMsg.check_calendar_date(message)
    if check_in_date:
        HandleSearchMsg.check_in(message.chat.id, message.from_user.id,
                                 check_in_date, LuxurySearchStates.check_out_date)


@bot.callback_query_handler(func=lambda call: call,
                            state=LuxurySearchStates.check_out_date)
def luxury_check_out_date_state_cb(call: CallbackQuery) -> None:
    """
    Catching state: LuxurySearchStates.check_out_date with callback query
    from a callback button (except "Zoom out", "previous year", "next year",
    "Previous month" or "Next month")  in calendar inline keyboard and calling
    HandleSearchMsg.check_out() for handling it if there is check out date.

    :param call: user reply data
    :type call: CallbackQuery
    """

    check_out_date = HandleSearchMsg.check_calendar_callback(call)
    if check_out_date:
        HandleSearchMsg.check_out(call.message.chat.id, call.from_user.id,
                                  check_out_date, LuxurySearchStates.travellers)


@bot.message_handler(state=LuxurySearchStates.check_out_date)
def luxury_check_out_date_state_msg(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.check_out_date and calling
    HandleSearchMsg.check_out() for handling it if check out date passed check
    in HandleSearchMsg.check_calendar_date().

    :param message: user reply data
    :type message: Message
    """

    check_out_date = HandleSearchMsg.check_calendar_date(message)
    if check_out_date:
        HandleSearchMsg.check_out(message.chat.id, message.from_user.id,
                                  check_out_date, LuxurySearchStates.travellers)


@bot.message_handler(state=LuxurySearchStates.travellers)
def luxury_travellers_state(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.travellers and calling
    HandleSearchMsg.set_travellers() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.set_travellers(message.chat.id, message.from_user.id,
                                   message.text, LuxurySearchStates.hotels_amount)


@bot.message_handler(state=LuxurySearchStates.hotels_amount)
def luxury_hotel_amount_state(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.hotels_amount and calling
    HandleSearchMsg.set_hotel_amount() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.set_hotel_amount(message.chat.id, message.from_user.id,
                                     message.text, LuxurySearchStates.hotels_photo)


@bot.message_handler(state=LuxurySearchStates.hotels_photo)
def luxury_photo_state(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.hotels_photo and calling
    HandleSearchMsg.show_hotel_photo() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.show_hotel_photo(message.chat.id, message.from_user.id,
                                     message.text, LuxurySearchStates.hotels_photo_amount)


@bot.message_handler(state=LuxurySearchStates.hotels_photo_amount)
def luxury_photo_amount_state(message: Message) -> None:
    """
    Catching state: LuxurySearchStates.hotels_photo_amount and calling
    HandleSearchMsg.set_photos_amount() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleSearchMsg.set_photos_amount(message.chat.id,
                                      message.from_user.id, message.text)
