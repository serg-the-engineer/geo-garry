from typing import Tuple, List, Optional, cast, Union, Dict, Any

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
                'Не удалось получить расстояние из переданных координат',
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
        api_response = self.gmaps_client.directions(point, destination)
        try:
            return cast(List[dict], api_response[0]['legs'][0]['steps'])
        except KeyError:
            logger.warning(
                'Не удалось получить маршрут из полученных данных',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_coordinates=destination,
                    gmaps_origin=point
                ),
            )
            return []

    def get_coordinates(self, place: str) -> Optional[Tuple[float, float]]:
        api_response = self.gmaps_client.geocode(
            place,
            language="ru",
        )
        if not api_response:
            logger.warning(
                'Геокодирование адреса вернуло пустой ответ',
                extra=dict(gmaps_place=place)
            )
            return None
        try:
            coordinates = api_response[0]['geometry']['location']
        except KeyError:
            logger.warning(
                'Неожиданный формат ответа от gmaps',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_place=place
                )
            )
            return None
        return coordinates['lat'], coordinates['lng']

    def get_address_components(self, coordinates: Tuple[float, float]) -> List[dict]:
        api_response = self.gmaps_client.reverse_geocode(
            coordinates,
            language="ru",
            result_type='street_address|bus_station|transit_station'
        )
        if not api_response:
            logger.warning(
                'Геокодирование координат вернуло пустой ответ',
                extra=dict(gmaps_coordinates=coordinates)
            )
            return []
        try:
            return cast(List[dict], api_response[0]['address_components'])
        except KeyError:
            logger.warning(
                'Неожиданный формат ответа от gmaps',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_coordinates=coordinates
                )
            )
            return []

    def get_coordinates_and_address_components(self, place: str) -> Optional[Dict[str, Any]]:
        api_response = self.gmaps_client.geocode(
            place,
            language="ru",
        )
        if not api_response:
            logger.warning(
                'Геокодирование адреса вернуло пустой ответ',
                extra=dict(gmaps_place=place)
            )
            return None
        try:
            coordinates = api_response[0]['geometry']['location']
            address_components = cast(List[dict], api_response[0]['address_components'])
        except KeyError:
            logger.warning(
                'Неожиданный формат ответа от gmaps',
                extra=dict(
                    gmaps_response=api_response,
                    gmaps_place=place
                )
            )
            return None
        return {
            'coordinates': (coordinates['lat'], coordinates['lng']),
            'address_components': address_components
        }


Schema = List[Union[List, Tuple, str]]
GOOGLE_MAPS_ADDRESS_SCHEMAS: Dict[str, Schema] = {
    'as_desc_string': [  # Returns address build from most specific to least specific
        (
            'locality',
            [
                'administrative_area_level_1',
                'administrative_area_level_2',
                'administrative_area_level_3',
            ],
        ),
        (
            [
                'route',
                'street_number',
            ],
            'bus_station',
            'transit_station',
        ),
    ],
    'federal_subject': [
        (
            'administrative_area_level_1',
            'administrative_area_level_2',
            'administrative_area_level_3',
            'locality',
        ),
    ],
    'city': [
        'locality',
    ]
}


class GoogleMapsAddress:
    TERMS = (
        'country',
        'locality',                     # город
        'administrative_area_level_1',  # обычно область
        'administrative_area_level_2',  # обычно район или город
        'administrative_area_level_3',
        'route',
        'street_number',
        'bus_station',
        'transit_station',
    )
    default_schema = GOOGLE_MAPS_ADDRESS_SCHEMAS['as_desc_string']

    def __init__(self, address_components: List[dict]):
        self.components: dict = dict()
        for component in address_components:
            for component_type in component.get('types', []):
                if component_type in self.TERMS:
                    self.components[component_type] = component.get('long_name', '').replace(chr(769), '')
                    continue

    def _handle_term(self, term) -> List[str]:
        if isinstance(term, str) and term in self.components:
            if term in ['bus_station', 'transit_station']:
                return ['ост. ' + self.components[term]]
            return [self.components[term]]
        if isinstance(term, list):
            subresult: List[str] = []
            for subterm in term:
                subresult += self._handle_term(subterm)
            return subresult
        if isinstance(term, tuple):
            for subterm in term:
                subresult = self._handle_term(subterm)
                if subresult:
                    return subresult
        return []

    def format(self, terms_schema: Schema = None) -> str:
        """
            Build string defined in terms_schema.
            If term not present it skipped. If term type differs from List, Tuple, Str it skipped
            Use list for logical AND and tuple for logical OR.
        """
        if not terms_schema or not isinstance(terms_schema, list):
            terms_schema = self.default_schema

        result: List[str] = []
        for term in terms_schema:
            result += self._handle_term(term)
        return ', '.join(result)
