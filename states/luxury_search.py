"""Module contain hotel search states for command 'high_price' """

from telebot.handler_backends import State, StatesGroup


class LuxurySearchStates(StatesGroup):
    """
    Class LuxurySearchStates.
    Parent Class (telebot.handler_backends.StatesGroup)
    Class for Top Luxury Search States scenario of command 'high_price'.

    Attributes:
        input_city (State): set city name where to search hotel
        confirm_city (State): confirm city name from suggested list
        check_in_date (State): set check in date
        check_out_date (State): set check out date
        travellers_amount (State): set number of travellers
        hotels_amount (State): set how many hotels to show
        hotels_photos_display (State): set hotels data with or without photos
        hotel_photos_amount(State): set number of hotels photos to display

    """
    input_city = State()
    confirm_city = State()
    check_in_date = State()
    check_out_date = State()
    travellers_amount = State()
    hotels_amount = State()
    hotels_photos_display = State()
    hotel_photos_amount = State()
