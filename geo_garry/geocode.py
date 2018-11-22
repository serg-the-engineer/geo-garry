import logging
from typing import Optional, Any, cast

from .cache import CacheStorageAbstract, CacheableServiceAbstractMixin
from .dataclasses import Coordinates
from .gmaps import GoogleMapsApi, GoogleMapsAddress

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Geocoder:
    def get_address(self, coordinates: Coordinates) -> str:
        """Return address string for provided coordinates."""
        raise NotImplementedError

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        """Return coordinates for provided address string."""
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
    def get_key(self, instance: Coordinates) -> str:
        return f'address:{round(instance.latitude, 4)},{round(instance.longitude, 4)}'

    def deserialize_value(self, value: bytes) -> str:
        return cast(str, value.decode())

    def serialize_value(self, value: Any) -> str:
        return value


class GmapsCacheableGeocodeService(CacheableServiceAbstractMixin):
    storage_class = CacheStorageCoordinates

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: str) -> Optional[Coordinates]:
        coordinates = self.api.get_coordinates(key)
        logger.info('Сервис GoogleMaps геокодировал адрес', address=key, coordinates=coordinates)
        return Coordinates(*coordinates) if coordinates else None


class GmapsCacheableReverseGeocodeService(CacheableServiceAbstractMixin):
    storage_class = CacheStorageAddress

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: Coordinates) -> Optional[str]:
        address_components = self.api.get_address_components(key.as_tuple())
        if not address_components:
            return None

        address = GoogleMapsAddress(address_components).format()
        logger.info('Сервис GoogleMaps перевел координаты в адрес', address=address, coordinates=key)
        return address


class GoogleGeocoder(Geocoder):

    def __init__(self, *, storage, api: GoogleMapsApi):
        self.api = api
        self.storage = storage

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        return GmapsCacheableGeocodeService(storage=self.storage, api=self.api).get(address)

    def get_address(self, coordinates: Coordinates) -> str:
        address = GmapsCacheableReverseGeocodeService(storage=self.storage, api=self.api).get(coordinates)

        if not address:
            address = coordinates.as_str()
        return address
