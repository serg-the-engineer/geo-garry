import logging
from typing import Tuple, List, Union, Dict
import requests


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

Schema = List[Union[List, Tuple, str]]


class OpenStreetMapsApi:
    def reverse(self, *, coordinates: Tuple[float, float], address_schema: Schema = None):
        raw_results = requests.get(  # type: ignore
            "https://nominatim.openstreetmap.org/reverse/",
            params={
                "format": "jsonv2",
                "lat": coordinates[0],
                "lon": coordinates[1],
                "accept-language": "ru",
            },
        ).json()
        return OpenStreetMapsAddress(raw_results).format(address_schema)


OSM_ADDRESS_SCHEMAS: Dict[str, Schema] = {
    'as_desc_string': [
        'state',
        'road',
        'building',
        'house_number',
    ],
    'federal_subject': [
        'state',
    ]
}

class OpenStreetMapsAddress:
    default_schema = OSM_ADDRESS_SCHEMAS['as_desc_string']

    def __init__(self, raw_results: Dict):
        self.address_components: Dict = raw_results.get('address', {})

    def match_state(self, state):
        state_aliases = {
            # "Кызылординская область": "Байконур",
            "Автономная Республика Крым": "Республика Крым",
        }

        return state_aliases.get(state, state)

    def format(self, terms_schema: Schema = None) -> str:
        """
            Build string defined in terms_schema.
            Term skipped if not present.
        """
        if not terms_schema or not isinstance(terms_schema, list):
            terms_schema = self.default_schema

        result: List[str] = []
        for term in terms_schema:
            val = self.address_components.get(term)
            if val:
                if term == 'state':
                    val = self.match_state(val)
                    if self.address_components.get('county') == 'Байконыр Г.А.':
                        val = 'Байконур'
                result.append(val)
        return ', '.join(result)
