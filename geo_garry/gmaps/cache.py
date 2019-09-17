from typing import cast, Any, Optional
from ..cache import CacheStorageAbstract, CacheNullStorageAbstract
from ..dataclasses import Coordinates, CoordinatesWithCity


class CacheStorageDistance(CacheStorageAbstract):

    def get_key(self, instance: Coordinates) -> str:
        return f'distance:{instance.as_str()}'

    def deserialize_value(self, value: bytes) -> float:
        return float(value)

    def serialize_value(self, value: int) -> str:
        return str(value)


class CacheStorageCoordinates(CacheNullStorageAbstract):
    """Cache calculated coordinates for address."""
    def get_key(self, instance: str) -> str:
        return f'coordinates:{instance}'

    def deserialize_value(self, value: bytes) -> Optional[Coordinates]:
        if not value:
            return None
        lat, lng = value.decode().split(',')
        return Coordinates(float(lat), float(lng))

    def serialize_value(self, value: Optional[Coordinates]) -> str:
        return value.as_str() if value else ''


class CacheStorageAddress(CacheStorageAbstract):
    """Cache calculated address for coordinates."""
    prefix = 'address'

    def get_key(self, instance: Coordinates) -> str:
        return f'{self.prefix}:{round(instance.latitude, 4)},{round(instance.longitude, 4)}'

    def deserialize_value(self, value: bytes) -> str:
        return cast(str, value.decode())

    def serialize_value(self, value: str) -> str:
        return value


class CacheStorageFederalSubject(CacheStorageAddress):
    """Cache calculated federal subject for coordinates."""
    prefix = 'federal'


class CacheStorageCoordinatesWithGeo(CacheNullStorageAbstract):
    """Cache calculated coordinates and geo_address for address."""
    def get_key(self, instance: str) -> str:
        return f'address_geo:{instance}'

    def deserialize_value(self, value: bytes) -> Optional[CoordinatesWithCity]:
        if not value:
            return None
        coords, geo = value.decode().split(';')
        lat, lng = coords.split(',')
        return CoordinatesWithCity(
            latitude=float(lat),
            longitude=float(lng),
            city=geo,
        )

    def serialize_value(self, value: Optional[CoordinatesWithCity]) -> str:
        return f'{value.as_str()};{value.city}' if value else ''
