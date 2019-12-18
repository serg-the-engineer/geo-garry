import logging
from typing import Optional
from ..cache import CacheableServiceAbstract
from ..dataclasses import Coordinates, CoordinatesAddress
from ..federal_subjects import FEDERAL_SUBJECT_CODES
from .api import GoogleMapsApi
from .address import GoogleMapsAddress, ADDRESS_SCHEMAS
from . import cache

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class GmapsCacheableGeocodeService(CacheableServiceAbstract):
    storage_class = cache.CacheStorageCoordinates

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def refresh_value(self, key: str) -> Optional[Coordinates]:
        coordinates_tuple = self.api.get_coordinates(key)
        if not coordinates_tuple:
            return None
        coordinates = Coordinates(*coordinates_tuple)
        logger.info(
            'Сервис GoogleMaps геокодировал адрес',
            extra=dict(
                geo_address=key,
                geo_coordinates=coordinates.as_str(),
            )
        )
        return coordinates

    def get_coordinates(self, address: str) -> Optional[Coordinates]:
        return self.get(address)


class GmapsCacheableReverseGeocodeService(CacheableServiceAbstract):
    storage_class = cache.CacheStorageAddress

    def __init__(self, *, storage, api: GoogleMapsApi):
        super().__init__(storage=storage)
        self.api = api

    def _get_data(self, key: Coordinates):
        return {
            'addresses': self.api.get_addresses(key.as_tuple()),
            'coordinates': key,
        }

    def refresh_value(self, key: Coordinates) -> Optional[CoordinatesAddress]:
        data = self._get_data(key)
        if not data:
            return None
        raw_addresses = data['addresses']
        coordinates = data['coordinates']
        if not raw_addresses or not isinstance(raw_addresses, list):
            return None

        google_address = GoogleMapsAddress(raw_addresses.pop(0))
        address = google_address.format(ADDRESS_SCHEMAS['as_desc_string'])
        city = google_address.format(ADDRESS_SCHEMAS['city'])
        federal_subject = google_address.format(ADDRESS_SCHEMAS['federal_subject'])
        federal_code = FEDERAL_SUBJECT_CODES.get(federal_subject)

        if not federal_code:
            while raw_addresses:
                google_address = GoogleMapsAddress(raw_addresses.pop(0))
                federal_subject = google_address.format(ADDRESS_SCHEMAS['federal_subject'])
                federal_code = FEDERAL_SUBJECT_CODES.get(federal_subject)
                if federal_code:
                    break

        logger.info(
            'Сервис GoogleMaps перевел координаты в адрес',
            extra=dict(
                geo_coordinates=coordinates.as_str(),
                geo_address=address,
                geo_city=city,
                geo_federal_code=federal_code,
            )
        )
        return CoordinatesAddress(
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
            address=address,
            city=city,
            federal_code=federal_code
        )

    def get_address(self, coordinates: Coordinates) -> Optional[str]:
        address_coordinates = self.get(coordinates)
        return address_coordinates.address if address_coordinates else None

    def get_federal_code(self, coordinates: Coordinates) -> Optional[int]:
        address_coordinates = self.get(coordinates)
        return address_coordinates.federal_code if address_coordinates else None

    def get_city(self, coordinates: Coordinates) -> Optional[str]:
        address_coordinates = self.get(coordinates)
        return address_coordinates.city if address_coordinates else None


class GmapsCacheableReverseByAddressService(GmapsCacheableReverseGeocodeService):
    storage_class = cache.CacheStorageAllByAddress

    def _get_data(self, key: str):
        data = self.api.get_coordinates_and_addresses(key)
        if not data:
            return None
        return {
            'addresses': data['addresses'],
            'coordinates': Coordinates(*data['coordinates']),
        }

    def get_geo(self, address: str) -> Optional[CoordinatesAddress]:
        return self.get(address)
