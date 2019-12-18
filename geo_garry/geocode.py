import logging
from typing import Optional

from .dataclasses import Coordinates, CoordinatesAddress
from .federal_subjects import FEDERAL_SUBJECT_CODES
from .osm import OpenStreetMapsApi, OSM_ADDRESS_SCHEMAS
from .gmaps.api import GoogleMapsApi
from .gmaps.geocode import (
    GmapsCacheableGeocodeService,
    GmapsCacheableReverseGeocodeService,
    GmapsCacheableReverseByAddressService,
)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Geocoder:
    def get_address(self, coordinates: Coordinates) -> Optional[str]:
        """Returns address string for provided coordinates."""
        raise NotImplementedError

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        """Returns coordinates for provided address string."""
        raise NotImplementedError

    def get_federal_code(self, coordinates: Coordinates) -> Optional[int]:
        """Returns region address component."""
        raise NotImplementedError


class GoogleGeocoder(Geocoder):

    def __init__(self, *, storage, gmaps_client):
        self.api = GoogleMapsApi(gmaps_client)
        self.storage = storage

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        return GmapsCacheableGeocodeService(storage=self.storage, api=self.api).get_coordinates(address)

    def get_address(self, coordinates: Coordinates) -> Optional[str]:
        service = GmapsCacheableReverseGeocodeService(storage=self.storage, api=self.api)
        return service.get_address(coordinates)

    def get_federal_code(self, coordinates: Coordinates) -> Optional[int]:
        service = GmapsCacheableReverseGeocodeService(storage=self.storage, api=self.api)
        return service.get_federal_code(coordinates)

    def get_geo(self, address: str) -> Optional[CoordinatesAddress]:
        """Return address coordinates and geocoded address by template."""
        service = GmapsCacheableReverseByAddressService(storage=self.storage, api=self.api)
        return service.get_geo(address)


class OpenStreetMapsGeocoder(Geocoder):
    def get_coordinates(self, address: str):
        raise NotImplementedError

    def get_address(self, coordinates: Coordinates) -> str:
        address = OpenStreetMapsApi().reverse(coordinates=coordinates.as_tuple())
        logger.info(
            'Сервис OSM перевел координаты в адрес',
            extra=dict(geo_address=address, geo_coordinates=coordinates.as_str())
        )
        return address

    def get_federal_code(self, coordinates: Coordinates) -> Optional[int]:
        federal_subject = OpenStreetMapsApi().reverse(
            coordinates=coordinates.as_tuple(),
            address_schema=OSM_ADDRESS_SCHEMAS['federal_subject']
        )
        federal_code = FEDERAL_SUBJECT_CODES.get(federal_subject)
        logger.info(
            'Сервис OSM перевел координаты в субъект',
            extra=dict(
                geo_federal_code=federal_code,
                geo_federal_subject=federal_subject,
                geo_coordinates=coordinates.as_str(),
            )
        )
        return federal_code

