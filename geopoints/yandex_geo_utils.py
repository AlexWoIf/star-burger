import requests
from django.conf import settings


def fetch_coordinates(address, apikey=settings.YANDEX_API_KEY):
    try:
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
    except Exception as e:
        # TODO: сделать различную обработку для различных видов ошибок (e)
        lon, lat = 0, 0
    return lon, lat
