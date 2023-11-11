from telebot.handler_backends import State, StatesGroup


class LuxurySearchStates(StatesGroup):
    """
    Class LuxurySearchStates.
    Parent Class (telebot.handler_backends.StatesGroup)
    Class for Top Luxury Search States scenario.

    Attributes:
        input_city (class State): state for inputting search city name
        confirm_city (class State): state for confirming search city name
        check_in_date (class State): state for inputting chick in date for
        hotels search
        check_out_date (class State): state for inputting chick out date for
        hotels search
        travellers (class State): state for inputting number of travellers for
        hotels search
        hotels_amount (class State): state for inputting number of hotels to search
        hotels_photo (class State): state for selecting response type with or
        without photos of hotel
        hotels_photo_amount(class State): state for inputting number of hotels
        photo to show  in telegram bot  response
    """

    input_city = State()
    confirm_city = State()
    check_in_date = State()
    check_out_date = State()
    travellers = State()
    hotels_amount = State()
    hotels_photo = State()
    hotels_photo_amount = State()
