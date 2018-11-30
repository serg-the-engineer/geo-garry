import logging
from typing import Optional, Any, cast, Dict, Union
from ..cache import CacheableServiceAbstractMixin
from ..dataclasses import Coordinates, CoordinatesWithCity
from .api import GoogleMapsApi, GoogleMapsAddress, GOOGLE_MAPS_ADDRESS_SCHEMAS
from . import cache

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class GmapsCacheableGeocodeService(CacheableServiceAbstractMixin):
    storage_class = cache.CacheStorageCoordinates

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: str) -> Optional[Coordinates]:
        coordinates = self.api.get_coordinates(key)
        logger.info(
            'Сервис GoogleMaps геокодировал адрес',
            extra=dict(address=key, coordinates=coordinates)
        )
        return Coordinates(*coordinates) if coordinates else None

    def get_coordinates(self, address: str):
        return self.get(address)


class GmapsCacheableReverseGeocodeService(CacheableServiceAbstractMixin):
    storage_class = cache.CacheStorageAddress
    address_schema = GOOGLE_MAPS_ADDRESS_SCHEMAS['as_desc_string']
    log_message = 'Сервис GoogleMaps перевел координаты в адрес'

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: Coordinates) -> Optional[str]:
        address_components = self.api.get_address_components(key.as_tuple())
        if not address_components:
            return None

        address = GoogleMapsAddress(address_components).format(self.address_schema)
        logger.info(self.log_message, extra=dict(address=address, coordinates=key))
        return address

    def get_address(self, coordinates: Coordinates):
        return self.get(coordinates)


class GmapsCacheableFederalSubjectService(GmapsCacheableReverseGeocodeService):
    storage_class = cache.CacheStorageFederalSubject
    address_schema = GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']
    log_message = 'Сервис GoogleMaps перевел координаты в субъект'

    def get_federal_subject(self, coordinates: Coordinates):
        return self.get(coordinates)


class GmapsCacheableAddressWithGeoService(CacheableServiceAbstractMixin):
    storage_class = cache.CacheStorageAddressWithGeo
    address_schema = GOOGLE_MAPS_ADDRESS_SCHEMAS['city']

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: str) -> Optional[CoordinatesWithCity]:
        result = self.api.get_coordinates_and_address_components(key)
        if result:
            coordinates = result['coordinates']
            city = GoogleMapsAddress(result['address_components']).format(self.address_schema)
            logger.info(
                'Сервис GoogleMaps геокодировал адрес',
                extra=dict(address=key, coordinates=coordinates, city=city)
            )
            return CoordinatesWithCity(
                latitude=coordinates[0],
                longitude=coordinates[1],
                city=city,
            )
        return None

    def get_address_with_city(self, address: str) -> Optional[CoordinatesWithCity]:
        return self.get(address)
