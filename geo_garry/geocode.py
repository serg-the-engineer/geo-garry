import logging
from typing import Optional

from .dataclasses import Coordinates
from .osm import OpenStreetMapsApi, OSM_ADDRESS_SCHEMAS
from .gmaps.api import GoogleMapsApi
from .gmaps.geocode import (
    GmapsCacheableGeocodeService,
    GmapsCacheableReverseGeocodeService,
    GmapsCacheableFederalSubjectService,
    GmapsCacheableAddressWithGeoService,
)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Geocoder:
    def get_address(self, coordinates: Coordinates) -> str:
        """Return address string for provided coordinates."""
        raise NotImplementedError

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        """Return coordinates for provided address string."""
        raise NotImplementedError

    def get_federal_subject(self, coordinates: Coordinates) -> str:
        """Return region address component."""
        raise NotImplementedError


class GoogleGeocoder(Geocoder):

    def __init__(self, *, storage, gmaps_client):
        self.api = GoogleMapsApi(gmaps_client)
        self.storage = storage

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        return GmapsCacheableGeocodeService(storage=self.storage, api=self.api).get_coordinates(address)

    def get_address(self, coordinates: Coordinates) -> str:
        service = GmapsCacheableReverseGeocodeService(storage=self.storage, api=self.api)
        address = service.get_address(coordinates)

        if not address:
            address = coordinates.as_str()
        return address

    def get_federal_subject(self, coordinates: Coordinates) -> str:
        service = GmapsCacheableFederalSubjectService(storage=self.storage, api=self.api)
        return service.get_federal_subject(coordinates)

    def get_address_with_city(self, address: str):
        """Return address coordinates and geocoded address by template."""
        service = GmapsCacheableAddressWithGeoService(storage=self.storage, api=self.api)
        return service.get_address_with_city(address)


class OpenStreetMapsGeocoder(Geocoder):
    def get_coordinates(self, address: str):
        raise NotImplementedError

    def get_address(self, coordinates: Coordinates) -> str:
        address = OpenStreetMapsApi().reverse(coordinates=coordinates.as_tuple())
        logger.info(
            'Сервис OSM перевел координаты в адрес',
            extra=dict(address=address, coordinates=coordinates.as_tuple)
        )
        return address

    def get_federal_subject(self, coordinates: Coordinates) -> str:
        address = OpenStreetMapsApi().reverse(
            coordinates=coordinates.as_tuple(),
            address_schema=OSM_ADDRESS_SCHEMAS['federal_subject']
        )
        logger.info(
            'Сервис OSM перевел координаты в субъект',
            extra=dict(address=address, coordinates=coordinates.as_tuple)
        )
        return address
