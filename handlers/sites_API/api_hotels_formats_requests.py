import requests
from pprint import pprint
import json


def get_meta_data():
    url = "https://hotels4.p.rapidapi.com/v2/get-meta-data"

    headers = {
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers).json()

    pprint(response)
    with open('get-meta-data.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


def location_search():

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": "new york"}

    headers = {
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()


    pprint(response)
    with open('locations_v3_search.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)

def location_not_exist_search():

    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": "pp"}

    headers = {
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring).json()


    pprint(response)
    with open('location_not_exist_search.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


def propertiesv2list():

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": "2621"},
        "checkInDate": {
            "day": 12,
            "month": 10,
            "year": 2023
        },
        "checkOutDate": {
            "day": 13,
            "month": 10,
            "year": 2023
        },
        "rooms": [
            {
                "adults": 2,
                "children": [{"age": 5}, {"age": 7}]
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 10,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 200,
            "min": 50
        }}
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    pprint(response)
    with open('properties_v2_list_NY.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


def get_content():

    url = "https://hotels4.p.rapidapi.com/properties/v2/get-content"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": "15838"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()

    pprint(response)
    with open('properties_v2_get_content.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)



def properties_v2_detail():

    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": "15838"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()

    with open('properties_v2_detail.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


def properties_v2_get_summery():
    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": "15838"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()

    with open('properties_v2_get_summery.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


# def properties_v2_get_offers():
#
#     #need to modify
#
#     url = "https://hotels4.p.rapidapi.com/properties/v2/get-offers"
#
#     payload = {
#         "currency": "USD",
#         "eapid": 1,
#         "locale": "en_US",
#         "siteId": 300000001,
#         "propertyId": "15838",
#         "checkInDate": {
#             "day": 12,
#             "month": 10,
#             "year": 2023
#         },
#         "checkOutDate": {
#             "day": 13,
#             "month": 10,
#             "year": 2023
#         },
#         "destination": {
#             "coordinates": {
#                 "latitude": 12.24959,
#                 "longitude": 109.190704
#             },
#             "regionId": "6054439"
#         },
#         "rooms": [
#             {
#                 "adults": 2,
#                 "children": [{"age": 5}, {"age": 7}]
#             },
#             {
#                 "adults": 2,
#                 "children": []
#             }
#         ]
#     }
#     headers = {
#         "content-type": "application/json",
#         "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#     }
#
#     response = requests.post(url, json=payload, headers=headers).json()
#
#     with open('properties_v2_get_offers', 'w', encoding='utf-8') as file:
#         json.dump(response, file, indent=4)


def reviews_v3_list():
    url = "https://hotels4.p.rapidapi.com/reviews/v3/list"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": "15838",
        "size": 10,
        "startingIndex": 0
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()


    with open('reviews_v3_list.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


def reviews_v3_get_summery():

    url = "https://hotels4.p.rapidapi.com/reviews/v3/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": "15838"
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "c50a57d185mshe0abc47f073683bp10153cjsn37c62de4ae65",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    with open('reviews_v3_get_summery.json', 'w', encoding='utf-8') as file:
        json.dump(response, file, indent=4)


