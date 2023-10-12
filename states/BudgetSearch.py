from telebot.handler_backends import State, StatesGroup


class BudgetSearchStates(StatesGroup):
    input_city = State()
    confirm_city = State()
    check_in_date = State()
    check_out_date = State()
    travellers = State()
    hotels_amount = State()
    hotels_photo = State()
    hotels_photo_amount = State()
    request_hotels = State()
    response_hotels = State()


