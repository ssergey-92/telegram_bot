"""Module contain hotel history states for command 'history' """

from telebot.handler_backends import State, StatesGroup


class HistoryStates(StatesGroup):
    """
    Class HistoryStates.
    Parent Class (telebot.handler_backends.StatesGroup)
    Class for user history search states scenario of command 'history'.

    Attributes:
        records_number (State): set number of history records to show

    """
    records_number = State()
