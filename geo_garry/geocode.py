import logging
from typing import Optional, Any, cast

from .cache import CacheStorageAbstract, CacheableServiceAbstractMixin
from .dataclasses import Coordinates
from .gmaps import GoogleMapsApi, GoogleMapsAddress, GOOGLE_MAPS_ADDRESS_SCHEMAS
from .osm import OpenStreetMapsApi, OSM_ADDRESS_SCHEMAS

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


class CacheStorageCoordinates(CacheStorageAbstract):
    def get_key(self, instance: str) -> str:
        return f'coordinates:{instance}'

    def deserialize_value(self, value: bytes) -> Coordinates:
        lat, lng = value.decode().split(',')
        return Coordinates(float(lat), float(lng))

    def serialize_value(self, value: Coordinates) -> str:
        return value.as_str()


class CacheStorageAddress(CacheStorageAbstract):
    prefix = 'address'

    def get_key(self, instance: Coordinates) -> str:
        return f'{self.prefix}:{round(instance.latitude, 4)},{round(instance.longitude, 4)}'

    def deserialize_value(self, value: bytes) -> str:
        return cast(str, value.decode())

    def serialize_value(self, value: Any) -> str:
        return value


class CacheStorageFederalSubject(CacheStorageAddress):
    prefix = 'federal'


class GmapsCacheableGeocodeService(CacheableServiceAbstractMixin):
    storage_class = CacheStorageCoordinates

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
    storage_class = CacheStorageAddress
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
    storage_class = CacheStorageFederalSubject
    address_schema = GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']
    log_message = 'Сервис GoogleMaps перевел координаты в субъект'

    def get_federal_subject(self, coordinates: Coordinates):
        return self.get(coordinates)


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
