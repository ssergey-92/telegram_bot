from telebot.handler_backends import State, StatesGroup


class CustomSearchStates(StatesGroup):
    input_city = State()
    confirm_city = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()
    check_in_date = State()
    check_out_date = State()
    travellers = State()
    hotels_amount = State()
    hotels_photo = State()
    hotels_photo_amount = State()