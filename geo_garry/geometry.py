from shapely.geometry import Point, Polygon, LineString

from .dataclasses import Coordinates


def get_line(point1: Coordinates, point2: Coordinates):
    return LineString([point1.as_tuple(), point2.as_tuple()])


def is_inside_polygon(coordinates: Coordinates, polygon: Polygon):
    """Tests if point inside polygon and not on the borders."""
    return polygon.contains(Point(coordinates.latitude, coordinates.longitude)) and not \
        polygon.touches(Point(coordinates.latitude, coordinates.longitude))


def get_part_outside_polygon(line: LineString, polygon: Polygon) -> float:
    return float(line.difference(polygon).length) / float(line.length)
