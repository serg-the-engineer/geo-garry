from typing import Tuple, List, Union, Dict


Schema = List[Union[List, Tuple, str]]
ADDRESS_SCHEMAS: Dict[str, Schema] = {
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
    default_schema = ADDRESS_SCHEMAS['as_desc_string']

    def __init__(self, address_components: List[dict]):
        self.components: dict = {}
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
            Builds string defined in terms_schema.
            Skipped if term does not exists or term type differs from List, Tuple, Str
            Use list for logical AND and tuple for logical OR.
        """
        if not terms_schema or not isinstance(terms_schema, list):
            terms_schema = self.default_schema

        result: List[str] = []
        for term in terms_schema:
            result += self._handle_term(term)
        return ', '.join(result)
