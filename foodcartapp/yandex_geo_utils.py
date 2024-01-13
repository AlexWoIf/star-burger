import requests
from geopy import distance
from django.conf import settings

def fetch_coordinates(address, apikey=settings.YANDEX_API_KEY):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = (
        response.json()['response']['GeoObjectCollection']['featureMember']
    )

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def distance_between(addr1, addr2):
    lon1, lat1 = fetch_coordinates(addr1)
    lon2, lat2 = fetch_coordinates(addr2)
    return distance.distance((lat1, lon1), (lat2, lon2))
