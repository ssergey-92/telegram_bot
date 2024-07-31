"""Module for communication with Hotels API"""

from datetime import datetime
from json import dump
from os import mkdir, path, getenv
from requests import get, post, exceptions
from typing import Optional

import backoff

from config_data.config import (
    HIGH_PRICE_COMMAND_DATA,
    LOW_PRICE_COMMAND_DATA,
)
from handlers.messages.utils.state_data import StateData
from project_logging.bot_logger import bot_logger

file_dir_abs_path = path.abspath(path.dirname(__file__))
response_files_abs_path = path.join(
    file_dir_abs_path, "./hotels_response_files",
)
bot_logger.debug(response_files_abs_path)
if not path.exists(response_files_abs_path):
    mkdir(response_files_abs_path)


class HotelsApi:
    """
    Base Class HotelsApi.
    Class for handling request and responses with website
    https://rapidapi.com/apidojo/api/hotels4/

    Attributes:
        _base_url (str): Hotels base url
        _rapid_api_key (str): Rapid API key
        _headers_get (dict): headers for get request to hotels
        _headers_post (dict): headers for post request to hotels
        _file_name (str): name of file for saving json response
        _response_files_dir (str): dir path for _file_name
        _find_city_endpoint (str): endpoint for searching cities
        _find_hotels_endpoint (str): endpoint for searching hotels_in_city
        _get_hotel_details_endpoint (str): endpoint to get extra hotel details
        _request_timeout (int): request timeout
        _backoff_exceptions (tuple): exceptions for backoff
        _backoff_max_time (int): maximum backoff time
        _backoff_max_tries (int): maximum backoff tries

    """

    _base_url = url = "https://hotels4.p.rapidapi.com/"
    _rapid_api_key = getenv("RAPID_API_KEY")
    _headers_get = {
        "X-RapidAPI-Key": _rapid_api_key,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    }
    _headers_post = {
        "content-type": "application/json",
        "X-RapidAPI-Key": _rapid_api_key,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    }
    _file_name = "{user_id}_{city_or_hotel}_{method}_{datetime}.json"
    _response_files_dir = response_files_abs_path
    _suitable_city_types = ["CITY", "NEIGHBORHOOD", "MULTIREGION"]
    _find_city_endpoint = "locations/v3/search"
    _find_hotels_endpoint = "properties/v2/list"
    _get_hotel_details_endpoint = "properties/v2/detail"
    _request_timeout = 10
    _backoff_exceptions = (exceptions.Timeout, exceptions.ConnectionError)
    _backoff_max_time = 20
    _backoff_max_tries = 2

    @classmethod
    def find_city(cls, user_id: int, city_name: str) -> list[Optional[dict]]:
        """Search matching cities based on city name.

        Send get request, save response, sort found cities and return them.

        Args:
             user_id (int): user identifier
             city_name (str): city name for search

        Returns:
            list[Optional[dict]]: matching cities

        """
        found_cities = HotelsApi._get_matching_cities(city_name)
        file_name = cls._file_name.format(
            user_id=user_id,
            city_or_hotel=city_name,
            method=cls.find_city.__name__,
            datetime=datetime.now(),
        )
        cls._save_response(file_name, found_cities)
        if found_cities and found_cities.get("sr"):
            sorted_cities = cls._sort_found_cities(found_cities["sr"])
        else:
            sorted_cities = []
        bot_logger.debug(f"{user_id=}, {city_name=}, {sorted_cities=}")
        return sorted_cities

    @classmethod
    def find_hotels_in_city(
        cls, chat_id: int, user_id: int
    ) -> list[Optional[dict]]:
        """Find hotels in city based on user search settings.

        Send POST request, save response, sort found hotels, add extra hotels
        data as per search settings.

        Args:
            chat_id (int): chat identifier
            user_id (int): user identifier

        Returns:
            list[Optional[dict]]: hotels details

        """
        search_settings = StateData.get_full_user_data(chat_id, user_id)
        found_hotels = HotelsApi._get_hotels_in_city(search_settings)
        file_name = cls._file_name.format(
            user_id=user_id,
            city_or_hotel=search_settings["full_name"],
            method=cls.find_hotels_in_city.__name__,
            datetime=datetime.now(),
        )
        cls._save_response(file_name, found_hotels)
        hotels_data = []
        if found_hotels and found_hotels.get("data"):
            hotels_data = cls._sort_hotels_in_city(
                found_hotels["data"], search_settings,
            )
            if hotels_data:
                hotels_data = cls._add_extra_hotels_data(
                    user_id, search_settings, hotels_data,
                )
        bot_logger.debug(f"{search_settings=}, {hotels_data=}")
        return hotels_data

    @classmethod
    def _save_response(cls, file_name: str, data: dict) -> None:
        """Save response data in json file.

        Args:
            file_name(str): file name
            data (dict): data to save

        """
        bot_logger.debug(f"{file_name=}")
        file_path = path.join(cls._response_files_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            dump(data, file, indent=4)

    @classmethod
    @backoff.on_exception(
        backoff.expo,
        exception=_backoff_exceptions,
        max_time=_backoff_max_time,
        max_tries=_backoff_max_tries,
    )
    def _get_matching_cities(cls, city_name: str) -> dict:
        """Send GET request to find cities as per city name.

        Args:
            city_name (str): city name for search

        Returns:
            dict: response

        """
        response = get(
            url=cls._base_url + cls._find_city_endpoint,
            params={"q": city_name},
            headers=cls._headers_get,
            timeout=cls._request_timeout,
        )
        bot_logger.debug(f"{city_name=}, {response.status_code=}")
        return response.json()

    @classmethod
    def create_hotel_search_payload(cls, search_settings: dict) -> dict:
        """Create payload for POST request of hotel search.

        Args:
            search_settings (dict): hotel search settings details

        Returns:
            dict: payload

        """
        payload = {
            "currency": "USD",
            "destination": {"regionId": search_settings["region_id"]},
            "checkInDate": search_settings["check_in_date"],
            "checkOutDate": search_settings["check_out_date"],
            "rooms": [{"adults": search_settings["adults"], "children": []}],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": search_settings["sort"],
            "filters": {
                "price": {
                    "max": search_settings["max_price"],
                    "min": search_settings["min_price"],
                },
                "availableFilter": "SHOW_AVAILABLE_ONLY",
            },
        }
        bot_logger.debug(f"{payload=}")
        return payload

    @classmethod
    @backoff.on_exception(
        backoff.expo,
        exception=_backoff_exceptions,
        max_tries=_backoff_max_tries,
        max_time=_backoff_max_time,
    )
    def _get_hotels_in_city(cls, search_settings: dict) -> dict:
        """Send POST request to find hotels in city.

        Args:
            search_settings (dict): hotel search settings details

        Returns:
            dict: response

        """
        response = post(
            url=cls._base_url + cls._find_hotels_endpoint,
            json=cls.create_hotel_search_payload(search_settings),
            headers=cls._headers_post,
            timeout=cls._request_timeout,
        )
        bot_logger.debug(f"{search_settings=}, {response.status_code=}")
        return response.json()

    @classmethod
    @backoff.on_exception(
        backoff.expo,
        exception=_backoff_exceptions,
        max_time=_backoff_max_time,
        max_tries=_backoff_max_tries,
    )
    def _get_hotel_details(cls, hotel_id: str) -> dict:
        """Send POST request to get hotel details.

        Args:
            hotel_id(str): unic hotel id

        Returns:
            dict: response

        """
        response = post(
            url=cls._base_url + cls._get_hotel_details_endpoint,
            json={"currency": "USD", "propertyId": hotel_id},
            headers=cls._headers_post,
            timeout=cls._request_timeout,
        )
        bot_logger.debug(f"{hotel_id=}, {response.status_code=}")
        return response.json()

    @classmethod
    def _sort_extra_hotel_data(
        cls, extra_details: dict, require_photos: bool, photo_amount: int,
    ) -> dict:
        """Sort extra hotel details.

        Args:
            extra_details (dict): extra hotel details to sort
            param require_photos (bool): True if include hotel photos
            param photo_amount (int):  number of hotel photos to include

        Returns:
            dict: sorted extra hotel details

        """
        hotel_info = extra_details["data"]["propertyInfo"]
        hotel_rating = "not rated"
        site_url = "not provided"
        photos_urls = list()
        if require_photos:
            photo_amount = min(
                photo_amount,
                len(hotel_info["propertyGallery"]["images"]),
            )
            for index in range(photo_amount):
                photos_urls.append(
                    hotel_info["propertyGallery"]["images"][index]["image"]["url"]
                )
        if hotel_info["summary"]["overview"]["propertyRating"]:
            hotel_rating = hotel_info["summary"]["overview"]["propertyRating"]["rating"]
        if site_url.startswith("https"):
            site_url = hotel_info["summary"]["name"]
        sorted_extra_data = {
            "site_url": site_url,
            "hotel_address": hotel_info["summary"]["location"]["address"]["addressLine"],
            "hotel_rating": hotel_rating,
            "photos_url": photos_urls,
        }
        bot_logger.debug(f"{hotel_info=}, {sorted_extra_data=}")
        return sorted_extra_data

    @classmethod
    def _add_extra_hotels_data(
        cls, user_id: int, search_settings: dict, hotels_data: list[dict],
    ) -> list[dict]:
        """Add extra hotel data as per search settings.

        Args:
            user_id (int): user identifier
            search_settings (dict): hotel search settings
            hotels_data (list[dict]): hotels data

        Returns:
            dict: hotels data with extra data if found

        """
        bot_logger.debug(f"{search_settings=}, {hotels_data=}")
        for index, i_hotel in enumerate(hotels_data):
            extra_hotel_data = cls._get_hotel_details(i_hotel["property_id"])
            file_name = cls._file_name.format(
                user_id=user_id,
                city_or_hotel=i_hotel["name"],
                method=cls._add_extra_hotels_data.__name__,
                datetime=datetime.now(),
            )
            cls._save_response(file_name, extra_hotel_data)
            sorted_extra_hotel_data = cls._sort_extra_hotel_data(
                extra_hotel_data,
                search_settings["display_hotel_photos"],
                search_settings["hotel_photo_amount"],
            )
            hotels_data[index].update(sorted_extra_hotel_data)
        bot_logger.debug(f"{hotels_data=}")
        return hotels_data

    @classmethod
    def _sort_found_cities(cls, cities_data: list) -> list[Optional[dict]]:
        """Sort found cities.

        Create cities list as per city types, include names and regions id.

        Args:
            cities_data: cities data from response

        Returns:
            list[dict]: cities details

        """
        sorted_cities_data = list()
        try:
            for i_city in cities_data:
                if i_city["type"] in cls._suitable_city_types:
                    required_city_data = {
                        "region_id": i_city["gaiaId"],
                        "full_name": i_city["regionNames"]["fullName"],
                    }
                    sorted_cities_data.append(required_city_data)
            bot_logger.debug(f"{sorted_cities_data=}")
            return sorted_cities_data
        except (KeyError, TypeError) as exc:
            bot_logger.debug(f"{exc=}")
            return []

    @classmethod
    def _sort_main_hotel_details(cls, hotel_details: dict) -> dict:
        """Sort hotel details from hotels search in city.

        Args:
            hotel_details (dict): hotel details from hotels search in city

        Returns:
            list[dict]: hotel details

        """
        try:
            distance = "{distance} {unit}".format(
                distance=hotel_details["destinationInfo"]["distanceFromDestination"]["value"],
                unit=hotel_details["destinationInfo"]["distanceFromDestination"]["unit"],
            )
            price_per_day = "{price} {currency}".format(
                price=round(hotel_details["price"]["lead"]["amount"], 2),
                currency=hotel_details["price"]["lead"]["currencyInfo"]["code"],
            )
            price_per_stay = hotel_details["price"]["displayMessages"][1]["lineItems"][0]["value"]
            price_per_stay = price_per_stay.replace(
                "total", "including all taxes",
            )
            sorted_hotel_details = {
                "name": hotel_details["name"],
                "property_id": hotel_details["id"],
                "distance": distance,
                "price_per_day": price_per_day,
                "price_per_stay": price_per_stay,
            }
            bot_logger.debug(f"{sorted_hotel_details=}")
            return sorted_hotel_details
        except (KeyError, TypeError, ValueError) as exc:
            bot_logger.debug(f"{exc=}")
            return {}

    @classmethod
    def _sort_hotels_for_low_price_cmd(
            cls, hotels_details: list[dict],
    ) -> list[dict]:
        """Sort found hotels in city as per low price command shortcut.

        Args:
            hotels_details (list[dict]): main hotels details

        Returns:
            list[dict]: sorted hotels details

        """
        sorted_hotels = []
        for i_hotel in hotels_details:
            sorted_hotels.append(cls._sort_main_hotel_details(i_hotel))
        bot_logger.debug(f"{sorted_hotels=}")
        return sorted_hotels

    @classmethod
    def _sort_hotels_for_high_price_cmd(
        cls, hotels_details: list[dict], required_hotels: int,
    ) -> list[dict]:
        """Sort found hotels in city as per high price command shortcut.

        Hotels details are sorted as per price ASC.

        Args:
            hotels_details (list[dict]): main hotels details
            required_hotels (int): required hotels amount

        Returns:
            list[dict]: sorted hotels details

        """
        sorted_hotels = []
        start_index = len(hotels_details) - 1
        stop_index = start_index - required_hotels
        step_range = -1
        for index in range(start_index, stop_index, step_range):
            sorted_hotels.append(
                cls._sort_main_hotel_details(hotels_details[index])
            )
        bot_logger.debug(f"{sorted_hotels=}")
        return sorted_hotels

    @classmethod
    def _is_hotel_as_per_search_settings(
            cls, hotel_details: dict, user_data: dict
    ) -> bool:
        """Check that main hotel data as per user search settings.

        Args:
            hotel_details (dict): main hotels details
            user_data (dict): user search settings

        Returns:
            bool: True if hotel is per search settings, False otherwise

        """
        try:
            user_min_price = user_data["min_price"]
            user_max_price = user_data["max_price"]
            user_min_distance = user_data["min_distance"]
            user_max_distance = user_data["max_distance"]
            price_per_day = hotel_details["price"]["lead"]["amount"]
            distance = hotel_details["destinationInfo"]["distanceFromDestination"]["value"]
            if (
                    user_min_price <= price_per_day <= user_max_price
                    and user_min_distance <= distance <= user_max_distance
            ):
                matching = True
            else:
                matching = False
            bot_logger.debug(f"{hotel_details['name']=}, {matching=}")
            return matching
        except (KeyError, TypeError, ValueError) as exc:
            bot_logger.debug(f"{exc=}")

    @classmethod
    def _sort_hotels_for_best_deal_cmd(
        cls, hotels_details: list[dict], user_data: dict,
    ) -> list[dict]:
        """Sort found hotels in city as per best deal command shortcut.

        Require additional check as HotelAPI provides all hotels in city if
        there is no hotel as per price range.

        Args:
            hotels_details (list[dict]): main hotels details
            user_data (dict): user search settings

        Returns:
            list[dict]: sorted hotels details

        """
        sorted_hotels = []
        for i_hotel in hotels_details:
            if cls._is_hotel_as_per_search_settings:
                sorted_hotels.append(cls._sort_main_hotel_details(i_hotel))
        bot_logger.debug(f"{user_data=}, {sorted_hotels=}")
        return sorted_hotels

    @classmethod
    def _sort_hotels_in_city(
        cls, hotels_data: dict, user_data: dict,
    ) -> list[Optional[dict]]:
        """Sort found hotels in city as per hotel search bot command shortcut.

        Args:
            hotels_data (dict): found hotels data from hotels search in city
            user_data (dict): user search settings

        Returns:
            list[Optional[dict]]: sorted hotels details

        """
        try:
            hotels_details = hotels_data["propertySearch"]["properties"]
            hotels_amount = min(
                user_data["hotels_amount"], len(hotels_details),
            )
            if hotels_details:
                if user_data["command"] == HIGH_PRICE_COMMAND_DATA["shortcut"]:
                    sorted_hotels = cls._sort_hotels_for_high_price_cmd(
                        hotels_details, hotels_amount,
                    )
                elif user_data["command"] == LOW_PRICE_COMMAND_DATA["shortcut"]:
                    sorted_hotels = cls._sort_hotels_for_low_price_cmd(
                        hotels_details[:hotels_amount],
                    )
                else:
                    sorted_hotels = cls._sort_hotels_for_best_deal_cmd(
                        hotels_details[:hotels_amount], user_data,
                    )
                bot_logger.debug(f"{sorted_hotels=}")
                return sorted_hotels
        except (TypeError, IndexError, ValueError) as exc:
            bot_logger.debug(f"{exc=}")
            return []
