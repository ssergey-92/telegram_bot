"""Module to create and add calendar filters to bot."""

from telebot import types, AdvancedCustomFilter, TeleBot
from telebot.callback_data import CallbackData, CallbackDataFilter

calendar_factory = CallbackData("year", "month", prefix="calendar")
calendar_zoom = CallbackData("year", prefix="calendar_zoom")


class CalendarCallbackFilter(AdvancedCustomFilter):
    """
    Child class CalendarCallbackFilter.
    Parent class telebot.AdvancedCustomFilter.
    Class for checking if CallbackQuery is from primary calendar screen
    (part 1 of 2).

    Attributes:
        key (str): name of key for saving class in
            telebot.AdvancedCustomFilter.custom_filters
    """

    key = "calendar_config"

    def check(
        self, call: types.CallbackQuery, config: CallbackDataFilter
    ) -> bool:
        """Check call as per CallbackDataFilter.check()

        :return: True if call appropriates to specified config else False
        :rtype: bool
        """

        return config.check(query=call)


class CalendarZoomCallbackFilter(AdvancedCustomFilter):
    """
    Child class CalendarZoomCallbackFilter.
    Parent class telebot.AdvancedCustomFilter.
    Class for checking if CallbackQuery is from secondary calendar screen
    (part 2 of 2).

    Attributes:
        key (str): name of key for saving class in
            telebot.AdvancedCustomFilter.custom_filters
    """

    key = "calendar_zoom_config"

    def check(
        self, call: types.CallbackQuery, config: CallbackDataFilter
    ) -> bool:
        """  Check call as per CallbackDataFilter.check()

        :return: True if call appropriates to specified config else False
        :rtype: bool
        """

        return config.check(query=call)


def add_calendar_filters(bot: TeleBot) -> None:
    """Adding custom filters to telegram bot.

    Args:
        telegram bot (TeleBot): telegram bot

    """
    bot.add_custom_filter(CalendarCallbackFilter())
    bot.add_custom_filter(CalendarZoomCallbackFilter())
