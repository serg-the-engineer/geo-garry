from typing import Optional
from ..cache import CacheStorageAbstract, CacheNullStorageAbstract
from ..dataclasses import Coordinates, CoordinatesAddress


class CacheStorageDistance(CacheStorageAbstract):

    def get_key(self, instance: Coordinates) -> str:
        return f'distance:{instance.as_str()}'

    def deserialize_value(self, value: bytes) -> float:
        return float(value)

    def serialize_value(self, value: int) -> str:
        return str(value)


class CacheStorageCoordinates(CacheNullStorageAbstract):
    """Stores calculated coordinates for address."""
    def get_key(self, instance: str) -> str:
        return f'coordinates:{instance}'

    def deserialize_value(self, value: bytes) -> Optional[Coordinates]:
        if not value:
            return None
        lat, lng = value.decode().split(',')
        return Coordinates(float(lat), float(lng))

    def serialize_value(self, value: Optional[Coordinates]) -> str:
        return value.as_str() if value else ''


class CacheStorageAddress(CacheNullStorageAbstract):
    """Stores calculated address, city, federal_code for coordinates."""
    prefix = 'geo'

    def get_key(self, instance: Coordinates) -> str:
        return f'{self.prefix}:{round(instance.latitude, 4)},{round(instance.longitude, 4)}'

    def deserialize_value(self, value: bytes) -> Optional[CoordinatesAddress]:
        if not value:
            return None
        coords, address, city, federal_code = value.decode().split(';')
        lat, lng = coords.split(',')
        return CoordinatesAddress(
            latitude=float(lat),
            longitude=float(lng),
            address=address,
            city=city or None,
            federal_code=int(federal_code) if federal_code else None,
        )

    def serialize_value(self, value: CoordinatesAddress) -> str:
        return value.as_str() if value else ''


class CacheStorageAllByAddress(CacheStorageAddress):
    """
        CaStores calculated coordinates and geo_address for address.
        It's hard to find city from human typed address string.
    """
    def get_key(self, instance: str) -> str:
        return f'geo_by_address:{instance}'
