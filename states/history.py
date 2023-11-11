from telebot.handler_backends import State, StatesGroup


class HistoryStates(StatesGroup):
    """
    Class HistoryStates.
    Parent Class (telebot.handler_backends.StatesGroup)
    Class for user history search states scenario.

    Attributes:
        records_number (class State): state for inputting number of user hotel
         search history records
    """

    records_number = State()
