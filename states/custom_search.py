"""Module contain hotel search states for command 'best_deal' """

from telebot.handler_backends import State, StatesGroup


class CustomSearchStates(StatesGroup):
    """
    Class CustomSearchStates.
    Parent Class (telebot.handler_backends.StatesGroup)
    Class for Custom Search States scenario of command 'best_deal'.

    Attributes:
        input_city (State): set city name where to search hotel
        confirm_city (State): confirm city name from suggested list
        min_price (class State): set min hotel price per day
        max_price (class State): set max hotel price per day
        min_distance (class State): set min hotel distance from city center
        max_distance (class State): set max hotel distance from city center
        check_in_date (State): set check in date
        check_out_date (State): set check out date
        travellers_amount (State): set number of travellers
        hotels_amount (State): set how many hotels to show
        hotels_photos_display (State): set hotels data with or without photos
        hotel_photos_amount(State): set number of hotels photos to display

    """
    input_city = State()
    confirm_city = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    check_in_date = State()
    check_out_date = State()
    travellers_amount = State()
    hotels_amount = State()
    hotels_photos_display = State()
    hotel_photos_amount = State()
