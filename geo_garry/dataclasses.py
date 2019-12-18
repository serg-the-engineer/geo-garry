from typing import Tuple, Optional

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
class CoordinatesAddress(Coordinates):
    address: str
    city: Optional[str] = None
    federal_code: Optional[int] = None

    def as_str(self) -> str:
        return "{},{};{};{};{}".format(
            self.latitude, self.longitude,
            self.address,
            self.city or '',
            self.federal_code or '',
        )
