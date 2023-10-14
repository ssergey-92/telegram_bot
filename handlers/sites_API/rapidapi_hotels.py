import json
import jmespath
from requests import get, post
import os
import backoff
from json import dump
from config_data.config import RAPID_API_KEY
from pprint import pprint
from abc import ABC
base_url = url = "https://hotels4.p.rapidapi.com/"
headers = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


class HotelsApi(ABC):

    @staticmethod
    def search_city(user_id: int, input_city: str, command: str) -> list[dict]:
        response_data = HotelsApi._search_city_get_request(input_city)
        file_name = HotelsApi._create_json_file(user_id, command, input_city,
                                                HotelsApi.search_city.__name__, response_data)
        sorted_data = HotelsApi._sort_search_city_data(file_name)
        return sorted_data

    @staticmethod
    def get_hotels_in_city(self):
        pass

    @staticmethod
    def _search_city_get_request(input_city: str) -> dict:
        location_endpoint = "locations/v3/search"
        search_url = "{}{}".format(base_url, location_endpoint)
        querystring = {"q": input_city}
        response = get(url=search_url, headers=headers, params=querystring,
                       timeout=10).json()
        return response

    @staticmethod
    def _create_json_file(user_id: int, command: str, city_or_hotel: str,
                          method_name: str, response: dict) -> str:
        file_name = ("handlers/sites_API/hotels_response_files/{user_id}_{command}_"
                     "{city_or_hotel}_{method_name}.json").format(
            user_id=user_id,
            command=command,
            city_or_hotel=city_or_hotel,
            method_name=method_name)
        with open(file_name, 'w', encoding='utf-8') as file:
            dump(response, file, indent=4)
        return file_name

    @staticmethod
    def _sort_search_city_data(file_name: json) -> list[dict]:
        with open(file_name, 'r', encoding='utf-8') as data:
            json_data = json.load(data)
        city_type = ["CITY", "NEIGHBORHOOD"]
        sorted_data = list()
        for i_data in enumerate(json_data["sr"]):
            if i_data[1]["type"] in city_type:
                sorted_data.append({"regionId": i_data[1]["gaiaId"],
                                    "fullName": i_data[1]["regionNames"]["fullName"]})

        return sorted_data

    @staticmethod
    def _search_hotels_in_city(user_id: int, command: str, place_id: str,
                               city_name: str, sort: str, min_price: int, max_price: int,
                               check_in_date: dict, check_out_date: dict, travellers: int):
        location_endpoint = "properties/v2/list"
        search_url = "{}{}".format(base_url, location_endpoint)

        payload = {
            "currency": "USD",
            "destination": {"regionId": place_id},
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "rooms": [
                {
                    "adults": travellers,
                    "children": []
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": sort,
            "filters": {
                "price": {
                    "max": max_price,
                    "min": min_price
                },
                "availableFilter": "SHOW_AVAILABLE_ONLY"
            }
        }

        response = post(url=search_url, json=payload,
                        headers=headers, timeout=10).json()
        HotelsApi._create_json_file(user_id, command, city_name,
                                    HotelsApi._search_hotels_in_city.__name__, response)

    @staticmethod
    def _get_hotel_details():
        pass

# check_in_date = {"day": 15, "month": 10, "year": 2023}
# check_out_date = {"day": 20, "month": 10, "year": 2023}
# HotelsApi.search_hotels_in_city(7227, "2198", 'Madrid',
#                                 "PRICE_LOW_TO_HIGH", 1, 1000000,
#                                 {"day": 15, "month": 10, "year": 2023},
#                                 {"day": 20, "month": 10, "year": 2023},
#                                 2)
