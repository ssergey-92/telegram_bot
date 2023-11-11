from abc import ABC
from requests import get, post, exceptions
from typing import Union
from json import dump, load

import backoff

from config_data.config import RAPID_API_KEY, BOT_COMMANDS
from handlers.messages.utils.state_data import StateData

base_url = url = "https://hotels4.p.rapidapi.com/"

headers_get = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

headers_post = {
    "content-type": "application/json",
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


class HotelsApi(ABC):
    """
    Base Class HotelsApi.
    Class for handling request and responses with website
    https://rapidapi.com/apidojo/api/hotels4/
    """

    @staticmethod
    def check_city(user_id: int, input_city: str, command: str) -> list[dict]:
        """
        Checking and collecting possible cities details from
        https://rapidapi.com/apidojo/api/hotels4/. Returns possible cities details.

        :param user_id: User identifier
        :type : int
        :param input_city: city name inputted by user
        :type : str
        :param command: bot command
        :type command: str

        :return: hotels api response sorted data with cities details
        :rtype: list[dict]
        """

        response_data = HotelsApi._search_city_request(input_city)
        file_name = HotelsApi._create_json_file(user_id, command, input_city,
                                                HotelsApi.check_city.__name__, response_data)
        sorted_data = HotelsApi._sort_searched_cities(file_name)
        return sorted_data

    @staticmethod
    def find_hotels_in_city(chat_id: int, user_id: int) -> list[dict]:
        """
        Searching and collecting hotels details from
        https://rapidapi.com/apidojo/api/hotels4/. Returns hotels details
        if matched with user request settings or empty list.

        :param chat_id: Chat identifier
        :type chat_id: int
        :param user_id: User identifier
        :type user_id: int

        :return: hotels api response sorted data with hotels details
        :rtype: list[dict]
        """

        user_data = StateData.retrieve_full_data_by_id(chat_id, user_id)
        response_part1 = HotelsApi._search_hotels_request(user_data)
        file_name_part1 = HotelsApi._create_json_file(user_id,
                                                      user_data["command"],
                                                      user_data["fullName"],
                                                      "hotels_in_city",
                                                      response_part1)
        hotels_data_part1 = HotelsApi._sort_hotels_in_city(file_name_part1,
                                                           user_data)
        merged_hotel_data = list()
        if hotels_data_part1:
            for index, i_hotel in enumerate(hotels_data_part1):
                response_part2 = HotelsApi._get_hotel_details_request(i_hotel['property_id'])
                file_names_part2 = HotelsApi._create_json_file(user_id,
                                                               user_data["command"],
                                                               i_hotel['property_id'],
                                                               "hotel_details",
                                                               response_part2)
                hotel_data_part2 = HotelsApi._sort_hotel_details(file_names_part2,
                                                                 user_data["display_hotel_photos"],
                                                                 user_data["hotel_photo_amount"])
                merged_hotel_data.append(hotels_data_part1[index] | hotel_data_part2)

        return merged_hotel_data

    @staticmethod
    @backoff.on_exception(backoff.expo,
                          exception=(exceptions.Timeout, exceptions.ConnectionError),
                          max_time=60,
                          max_tries=2)
    def _search_city_request(input_city: str) -> dict:
        """
        Searching cites data in https://rapidapi.com/apidojo/api/hotels4/.
        (get request)

        :param input_city: city name
        :type input_city: str

        :return: hotels api response sorted data with cities details
        :rtype: dict
        """

        location_endpoint = "locations/v3/search"
        search_url = "{}{}".format(base_url, location_endpoint)
        querystring = {"q": input_city}
        response = get(url=search_url, headers=headers_get, params=querystring,
                       timeout=10)
        print(response)
        return response.json()

    @staticmethod
    @backoff.on_exception(backoff.expo,
                          exception=(exceptions.Timeout, exceptions.ConnectionError),
                          max_time=60,
                          max_tries=2)
    def _search_hotels_request(user_data: dict) -> dict:
        """
        Searching hotels in city in https://rapidapi.com/apidojo/api/hotels4/
        (post request)

        :param user_data: user search settings details
        :type user_data: dict

        :return: hotels api response sorted data with hotels details
        :rtype: dict
        """

        location_endpoint = "properties/v2/list"
        hotels_url = "{}{}".format(base_url, location_endpoint)
        payload = {
            "currency": "USD",
            "destination": {"regionId": user_data["regionId"]},
            "checkInDate": user_data["checkInDate"],
            "checkOutDate": user_data["checkOutDate"],
            "rooms": [
                {
                    "adults": user_data["adults"],
                    "children": []
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": user_data["sort"],
            "filters": {
                "price": {
                    "max": user_data["max_price"],
                    "min": user_data["min_price"]
                },
                "availableFilter": "SHOW_AVAILABLE_ONLY"
            }
        }
        response = post(url=hotels_url, json=payload,
                        headers=headers_post, timeout=10).json()
        return response

    @staticmethod
    @backoff.on_exception(backoff.expo,
                          exception=(exceptions.Timeout, exceptions.ConnectionError),
                          max_time=60,
                          max_tries=2)
    def _get_hotel_details_request(property_id: str) -> dict:
        """
        Searching hotel specific details in
        https://rapidapi.com/apidojo/api/hotels4/ (post request)

        :param property_id: unic hotel id
        :type property_id: str

        :return: hotels api response sorted data with hotel specific details
        :rtype: dict
        """

        hotel_detail_endpoint = "properties/v2/detail"
        hotel_details_url = "{}{}".format(base_url, hotel_detail_endpoint)
        payload = {
            "currency": "USD",
            "propertyId": property_id
        }
        response = post(url=hotel_details_url, json=payload,
                        headers=headers_post, timeout=10).json()
        return response

    @staticmethod
    def _create_json_file(user_id: int, command: str, city_or_hotel: str,
                          method_name: str, response: dict) -> str:
        """
        Creating json file.

        :param user_id: User identifier
        :type : int
        :param command: name of command shortcut
        :type : str
        :param city_or_hotel: name of city or hotel
        :type : str
        :param method_name: name of method
        :type : str
        :param response: data for writing in file
        :type : dict

        :return: json file name
        :rtype: str
        """

        file_name = ("handlers/sites_API/hotels_response_files/{user_id}"
                     "_{command}_{city_or_hotel}_{method_name}.json").format(
            user_id=user_id,
            command=command,
            city_or_hotel=city_or_hotel,
            method_name=method_name)
        with open(file_name, 'w', encoding='utf-8') as file:
            dump(response, file, indent=4)

        return file_name

    @staticmethod
    def _sort_searched_cities(file_name: str) -> list[dict]:
        """
        Sorting cities details as per city type(city_type) and extracting city id
         and full name.

        :param file_name: file name with cities details
        :type file_name: str

        :return: sorted data with cities details
        :rtype: list[dict]
        """

        with open(file_name, 'r', encoding='utf-8') as data:
            locations_data = load(data)
        sorted_data = list()
        if locations_data and locations_data.get("sr"):
            city_type = ["CITY", "NEIGHBORHOOD", "MULTIREGION"]
            for i_data in enumerate(locations_data["sr"]):
                if i_data[1]["type"] in city_type:
                    sorted_data.append({"regionId": i_data[1]["gaiaId"],
                                        "fullName": i_data[1]["regionNames"]["fullName"]})

        return sorted_data

    @staticmethod
    def _sort_hotels_in_city(file_name: str, user_data: dict) \
            -> Union[list, list[dict]]:
        """
        Sorting hotels in city details as per bot command shortcut ("Top Budget
        Hotels", "Top Luxury Hotels", "Custom Hotel Search").

        :param file_name: file name with cities details
        :type file_name: str

        :return: sorted data with hotels details(hotel name, hotel id, distance
        from city center, hotel  price per day and price per stay)
        :rtype: list[dict]
        """

        command = user_data["command"]
        with open(file_name, 'r', encoding='utf-8') as data:
            hotels_data = load(data)
        sorted_data = list()
        try:
            if hotels_data["data"]:
                properties_data = hotels_data["data"]["propertySearch"]["properties"]
                properties_list_len = len(properties_data)
                hotels_amount = min(user_data["hotels_amount"], properties_list_len)
                if command == BOT_COMMANDS[4][1]:  # top_luxury_hotels  shortcut
                    # settings for range due to available sort "LOW TO HIGH PRICE"
                    start_index = properties_list_len - 1
                    stop_index = start_index - hotels_amount
                    step_range = -1
                else:
                    start_index = 0
                    stop_index = hotels_amount
                    step_range = 1
                for index in range(start_index, stop_index, step_range):
                    distance_key = properties_data[index]["destinationInfo"][
                        "distanceFromDestination"]
                    distance_info = "{} {}".format(
                        distance_key["value"],
                        distance_key["unit"]
                    )
                    price_per_day = "{} {}".format(
                        round(properties_data[index]["price"]["lead"]["amount"], 2),
                        properties_data[index]["price"]["lead"]["currencyInfo"]["code"]
                    )
                    price_per_stay = properties_data[index]["price"]["displayMessages"][
                        1]["lineItems"][0]["value"]
                    price_per_stay = price_per_stay.replace('total', 'including all taxes')
                    sorted_data.append({"name": properties_data[index]["name"],
                                        "property_id": properties_data[index]["id"],
                                        "distance": distance_info,
                                        "price_per_day": price_per_day,
                                        "price_per_stay": price_per_stay}
                                       )
                if command == BOT_COMMANDS[5][1]:  # custom_hotel_search shortcut
                    # hotelAPI provides hole hotels data for city if there is no hotel
                    # as per price range
                    sorted_data = HotelsApi._custom_hotels_sort(sorted_data, user_data)
        except TypeError as exc:
            print(f'Sort hotels in city exception: {exc}')
        return sorted_data

    @staticmethod
    def _custom_hotels_sort(sorted_data: list[dict], user_data: dict
                            ) -> Union[list, list[dict]]:
        """
        Sorting hotels in city as per price and distance from city range and user
        required hotels quantity.

        :param sorted_data: sorted data with hotels details(hotel name, hotel id,
         distance, from city center, hotel  price per day and price per stay)
        :type sorted_data: list[dict]
        :param user_data: user search settings details
        :type user_data: dict

        :return: sorted hotels data
        :rtype: Union[list, list[dict]]
        """

        custom_data = list()
        for i_hotel in sorted_data:
            hotel_price_per_day = i_hotel["price_per_day"].split(' ')
            hotel_price_figure = float(hotel_price_per_day[0])
            if (user_data["min_price"] <= hotel_price_figure
                    <= user_data["max_price"]):
                hotel_distance = i_hotel["distance"].split(' ')
                hotel_distance_figure = float(hotel_distance[0])
                if (user_data["min_distance"] <= hotel_distance_figure
                        <= user_data["max_distance"]):
                    custom_data.append(i_hotel)
        return custom_data

    @staticmethod
    def _sort_hotel_details(file_name_part2: str, display_hotel_photo: str,
                            hotel_photo_amount: int) -> dict:
        """
        Extracting and making dict with hotel specific details.

        :param file_name_part2: file name with hotel details
        :type file_name_part2: str
        :param display_hotel_photo: answer yes/no for displaying hotel photos
        :type display_hotel_photo: str
        :param hotel_photo_amount:  displaying hotel photos amount
        :type hotel_photo_amount:int

        :return: sorted hotel specific details(hotel website, hotel address,
        hotel_rating, photos_url)
        :rtype: dict
        """

        with open(file_name_part2, 'r', encoding='utf-8') as data:
            hotel_details = load(data)
        hotel_info = hotel_details["data"]["propertyInfo"]
        photos_urls = list()
        hotel_rating = 'not rated'
        site_url = 'not provided'
        if display_hotel_photo.lower() == 'yes':
            hotel_photo_amount = min(hotel_photo_amount,
                                     len(hotel_info["propertyGallery"]["images"]))
            for index in range(hotel_photo_amount):
                photos_urls.append(hotel_info["propertyGallery"]["images"][index][
                                       "image"]["url"])
        if hotel_info["summary"]["overview"]["propertyRating"]:
            hotel_rating = hotel_info["summary"]["overview"]["propertyRating"]["rating"]
        if site_url.startswith('https'):
            site_url = hotel_info["summary"]["name"]
        data_part2 = {"site_url": site_url,
                      "hotel_address": hotel_info["summary"]["location"][
                          "address"]["addressLine"],
                      "hotel_rating": hotel_rating,
                      "photos_url": photos_urls}

        return data_part2
