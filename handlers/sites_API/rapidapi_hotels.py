import json
import jmespath
from requests import get, post
import os
import backoff
from json import dump

from config_data.config import RAPID_API_KEY
from handlers.messages.utils.state_data import retrieve_full_state_data_by_id
from pprint import pprint
from abc import ABC

base_url = url = "https://hotels4.p.rapidapi.com/"

headers_get = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

headers_post = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
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
        user_data = retrieve_full_state_data_by_id(chat_id, user_id)

        # command = user_data["command"]
        # sort = user_data["sort"]
        # city_name = user_data["fullName"]
        # place_id = user_data["regionId"]
        # check_in_date = user_data["checkInDate"]
        # check_out_date = user_data["checkOutDate"]
        # min_price = user_data["min_price"]
        # max_price = user_data["max_price"]
        # travellers = user_data["adults"]
        # hotels_amount = user_data["hotels_amount"]
        # display_hotel_photos = user_data["display_hotel_photos"]
        # hotel_photo_amount = user_data["hotel_photo_amount"]

        response_part1 = HotelsApi._search_hotels_request(user_id,
                                                          user_data)
        file_name_part1 = HotelsApi._create_json_file(user_id,
                                                      user_data["command"],
                                                      user_data["fullName"],
                                                      HotelsApi.find_hotels_in_city.__name__,
                                                      response_part1)
        hotels_data_part1 = HotelsApi._sort_hotels_in_city(file_name_part1,
                                                           user_data["hotels_amount"])
        merged_hotel_data = list()
        for index, i_hotel in enumerate(hotels_data_part1):
            response_part2 = HotelsApi._get_hotel_details_request(i_hotel['property_id'])
            file_names_part2 = HotelsApi._create_json_file(user_id,
                                                           user_data["command"],
                                                           i_hotel['property_id'],
                                                           HotelsApi.find_hotels_in_city.__name__,
                                                           response_part2)
            hotel_data_part2 = HotelsApi._sort_hotel_details(file_names_part2,
                                                             user_data["display_hotel_photos"],
                                                             user_data["hotel_photo_amount"])
            merged_hotel_data.append(hotels_data_part1[index] | hotel_data_part2)

        print(merged_hotel_data)
        return merged_hotel_data


    @staticmethod
    def _search_city_request(input_city: str) -> dict:
        location_endpoint = "locations/v3/search"
        search_url = "{}{}".format(base_url, location_endpoint)
        querystring = {"q": input_city}
        response = get(url=search_url, headers=headers_get, params=querystring,
                       timeout=10).json()

        return response

    @staticmethod
    def _search_hotels_request(user_id: int, user_data: dict) -> dict:
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
    def _sort_searched_cities(file_name: json) -> list[dict]:
        with open(file_name, 'r', encoding='utf-8') as data:
            locations_data = json.load(data)
        city_type = ["CITY", "NEIGHBORHOOD"]
        sorted_data = list()
        for i_data in enumerate(locations_data["sr"]):
            if i_data[1]["type"] in city_type:
                sorted_data.append({"regionId": i_data[1]["gaiaId"],
                                    "fullName": i_data[1]["regionNames"]["fullName"]})

        return sorted_data

    @staticmethod
    def _sort_hotels_in_city(file_name: str, hotels_amount: int) -> list[dict]:
        with open(file_name, 'r', encoding='utf-8') as data:
            hotels_data = json.load(data)
        sorted_data = list()
        properties_data = hotels_data["data"]["propertySearch"]["properties"]
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
            hotel_details = json.load(data)
        hotel_info = hotel_details["data"]["propertyInfo"]
        photos_urls = list()
        if display_hotel_photo.lower() == 'yes':
            for index in range(hotel_photo_amount):
                photos_urls.append(hotel_info["propertyGallery"]["images"][index][
                                       "image"]["url"])
        data_part2 = {"site_url": hotel_info["summary"]["name"],
                      "hotel_address": hotel_info["summary"]["location"][
                          "address"]["addressLine"],
                      "hotel_rating": hotel_info["summary"]["overview"][
                          "propertyRating"]["rating"],
                      "photos_url": photos_urls}

        return data_part2
