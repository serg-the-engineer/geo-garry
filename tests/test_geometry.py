from geo_garry import geometry, distance, polygons
from geo_garry.dataclasses import Coordinates


def test_is_inside_polygon():
    assert geometry.is_inside_polygon(
        Coordinates(latitude=55.6892209716432, longitude=37.752854389528585),
        polygons.MKAD_POLYGON,
    )
    assert not geometry.is_inside_polygon(
        Coordinates(latitude=50.4254225, longitude=36.9020654),
        polygons.MKAD_POLYGON,
    )
    assert geometry.is_inside_polygon(
        Coordinates(latitude=60.0321828248, longitude=30.4326002502),
        polygons.KAD_POLYGON,
    )
    assert not geometry.is_inside_polygon(
        Coordinates(latitude=55.6892209716432, longitude=30.4526002502),
        polygons.KAD_POLYGON,
    )

    # on the border - not in polygon
    assert not geometry.is_inside_polygon(
        Coordinates(latitude=55.77271261339107, longitude=37.843152686304705),
        polygons.MKAD_POLYGON,
    )


def test_line_outside_part():
    assert round(geometry.get_part_outside_polygon(
        geometry.get_line(
            Coordinates(latitude=59.992947, longitude=30.456704),
            Coordinates(latitude=59.998849, longitude=30.499904),
        ),
        polygons.KAD_POLYGON
    ), 1) == 0.5
