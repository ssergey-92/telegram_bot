from abc import ABC
from requests import get, post, exceptions
from json import dump, load

import backoff
from loguru import logger

from config_data.config import RAPID_API_KEY
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

    @staticmethod
    def check_city(user_id: int, input_city: str, command: str) -> list[dict]:
        response_data = HotelsApi._search_city_request(input_city)
        file_name = HotelsApi._create_json_file(user_id, command, input_city,
                                                HotelsApi.check_city.__name__, response_data)
        sorted_data = HotelsApi._sort_searched_cities(file_name)
        return sorted_data

    @staticmethod
    def find_hotels_in_city(chat_id: int, user_id: int) -> list[dict]:
        user_data = StateData.retrieve_full_data_by_id(chat_id, user_id)
        response_part1 = HotelsApi._search_hotels_request(user_data)
        file_name_part1 = HotelsApi._create_json_file(user_id,
                                                      user_data["command"],
                                                      user_data["fullName"],
                                                      "hotels_in_city",
                                                      response_part1)
        hotels_data_part1 = HotelsApi._sort_hotels_in_city(file_name_part1,
                                                           user_data["hotels_amount"])
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
        location_endpoint = "locations/v3/search"
        search_url = "{}{}".format(base_url, location_endpoint)
        querystring = {"q": input_city}
        response = get(url=search_url, headers=headers_get, params=querystring,
                       timeout=10).json()

        return response

    @staticmethod
    @backoff.on_exception(backoff.expo,
                          exception=(exceptions.Timeout, exceptions.ConnectionError),
                          max_time=60,
                          max_tries=2)
    def _search_hotels_request(user_data: dict) -> dict:
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
        with open(file_name, 'r', encoding='utf-8') as data:
            locations_data = load(data)
        sorted_data = list()
        if locations_data["sr"]:
            city_type = ["CITY", "NEIGHBORHOOD", "MULTIREGION"]
            for i_data in enumerate(locations_data["sr"]):
                if i_data[1]["type"] in city_type:
                    sorted_data.append({"regionId": i_data[1]["gaiaId"],
                                        "fullName": i_data[1]["regionNames"]["fullName"]})

        return sorted_data

    @staticmethod
    def _sort_hotels_in_city(file_name: str, hotels_amount: int) -> list[dict]:
        with open(file_name, 'r', encoding='utf-8') as data:
            hotels_data = load(data)
        sorted_data = list()
        if hotels_data["data"]:
            properties_data = hotels_data["data"]["propertySearch"]["properties"]
            hotels_amount = min(hotels_amount, len(properties_data))
            for index in range(hotels_amount):
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

        return sorted_data

    @staticmethod
    def _sort_hotel_details(file_name_part2: str, display_hotel_photo: str,
                            hotel_photo_amount: int) -> dict:
        with open(file_name_part2, 'r', encoding='utf-8') as data:
            hotel_details = load(data)
        hotel_info = hotel_details["data"]["propertyInfo"]
        photos_urls = list()
        hotel_rating = 'not rated'
        site_url = 'not exist'
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
