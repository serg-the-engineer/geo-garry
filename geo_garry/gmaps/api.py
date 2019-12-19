from typing import Tuple, List, Optional, cast, Dict, Generator, Union

import logging

# gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)  # pylint: disable=invalid-name

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class GoogleMapsApi:
    def __init__(self, gmaps_client):
        self.gmaps_client = gmaps_client

    def get_distance_from_points(
            self,
            origins: List[Tuple[float, float]],
            destination: Tuple[float, float],
    ) -> int:
        logger.debug(
            'Отправлен запрос GoogleMaps.distance_matrix',
            extra=dict(
                gmaps_coordinates=destination,
                gmaps_origins=origins
            ),
        )
        distance_matrix = self.gmaps_client.distance_matrix(
            origins=origins,
            destinations=destination,
            mode='driving',
        )

        try:
            return cast(int, min(
                [row['elements'][0]['distance']['value'] for row in distance_matrix['rows']]
            ))
        except KeyError:
            logger.warning(
                'Не удалось получить расстояние GoogleMaps из переданных координат',
                extra=dict(
                    gmaps_response=distance_matrix,
                    gmaps_coordinates=destination,
                    gmaps_origins=origins
                ),
            )
            return 0

    def get_driving_path(
            self,
            point: Tuple[float, float],
            destination: Tuple[float, float],
    ) -> List[dict]:
        logger.debug(
            'Отправлен запрос GoogleMaps.directions',
            extra=dict(
                gmaps_coordinates=destination,
                gmaps_origin=point
            ),
        )
        api_response = self.gmaps_client.directions(point, destination)
        try:
            return cast(List[dict], api_response[0]['legs'][0]['steps'])
        except KeyError:
            logger.warning(
                'Не удалось получить маршрут GoogleMaps из полученных данных',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_coordinates=destination,
                    gmaps_origin=point
                ),
            )
            return []

    def get_coordinates(self, place: str) -> Optional[Tuple[float, float]]:
        logger.debug(
            'Отправлен запрос GoogleMaps.geocode',
            extra=dict(gmaps_place=place)
        )
        api_response = self.gmaps_client.geocode(
            place,
            language="ru",
        )
        if not api_response:
            logger.warning(
                'Геокодирование адреса GoogleMaps вернуло пустой ответ',
                extra=dict(gmaps_place=place)
            )
            return None
        try:
            coordinates = api_response[0]['geometry']['location']
        except KeyError:
            logger.warning(
                'Неожиданный формат ответа от GoogleMaps',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_place=place
                )
            )
            return None
        return coordinates['lat'], coordinates['lng']

    def get_addresses(self, coordinates: Tuple[float, float]) -> Optional[Generator[List, None, None]]:
        logger.debug(
            'Отправлен запрос GoogleMaps.reverse_geocode',
            extra=dict(gmaps_coordinates=coordinates)
        )
        api_response = self.gmaps_client.reverse_geocode(
            coordinates,
            language="ru",
            result_type='street_address|bus_station|transit_station'
        )
        if not api_response:
            logger.warning(
                'Геокодирование координат GoogleMaps вернуло пустой ответ',
                extra=dict(gmaps_coordinates=coordinates)
            )
            return []
        return (
            address['address_components'] for address in api_response
        )

    def get_coordinates_and_addresses(self, place: str) -> Optional[Dict[str, Union[Tuple[int], Generator]]]:
        logger.debug(
            'Отправлен запрос GoogleMaps.geocode',
            extra=dict(gmaps_place=place)
        )
        api_response = self.gmaps_client.geocode(
            place,
            language="ru",
        )
        if not api_response:
            logger.warning(
                'Геокодирование адреса GoogleMaps вернуло пустой ответ',
                extra=dict(gmaps_place=place)
            )
            return None
        try:
            coordinates = api_response[0]['geometry']['location']
            addresses = (
                address['address_components'] for address in api_response
            )
        except KeyError:
            logger.warning(
                'Неожиданный формат ответа от GoogleMaps',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_place=place
                )
            )
            return None
        return {
            'coordinates': (coordinates['lat'], coordinates['lng']),
            'addresses': addresses
        }
