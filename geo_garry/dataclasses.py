from typing import Tuple

from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def as_str(self) -> str:
        return "{},{}".format(self.latitude, self.longitude)

    def as_tuple(self) -> Tuple[float, float]:
        return self.latitude, self.longitude


@dataclass(frozen=True)
class CoordinatesWithCity(Coordinates):
    city: str

    def get_coordinates_as_str(self) -> str:
        return
