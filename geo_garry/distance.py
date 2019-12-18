from typing import Tuple, List, Optional

import logging
from scipy.spatial import KDTree
from shapely.geometry import Polygon

from . import geometry
from .dataclasses import Coordinates
from .cache import CacheableServiceAbstract
from .gmaps.cache import CacheStorageDistance
from .gmaps.api import GoogleMapsApi
from .polygons import MKAD_POLYGON, KAD_POLYGON

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

PointTuple = Tuple[float, float]
MKAD_EXITS_COORDINATES = [
    (55.77682626803085, 37.84269989967345),
    (55.76903191638017, 37.84318651588698),
    (55.74392477931212, 37.84185519957153),
    (55.73052122580085, 37.84037898416108),
    (55.71863531207276, 37.83895012458452),
    (55.711831272333605, 37.83713368900962),
    (55.707901422046966, 37.8350106548768),
    (55.6869523798766, 37.83057993978087),
    (55.65692789667629, 37.83910426510268),
    (55.640528720308474, 37.819652386266085),
    (55.617789410062215, 37.782276430404394),
    (55.59175631830074, 37.72929474857808),
    (55.57581125568298, 37.687799514747375),
    (55.57272629492449, 37.65277241112271),
    (55.57605719591829, 37.59643530860042),
    (55.58106457666858, 37.57265144016032),
    (55.59150701569656, 37.52902190629794),
    (55.61120819157864, 37.49189413873337),
    (55.638972144200956, 37.45948542596951),
    (55.66189360804507, 37.432824164364256),
    (55.68278581583797, 37.416807425418966),
    (55.668026850906536, 37.42778473861195),
    (55.70188946767468, 37.39895204348993),
    (55.713602586285944, 37.38589295731531),
    (55.72348037785042, 37.38078139017449),
    (55.73175585229489, 37.37657178200628),
    (55.76508406345848, 37.36928736556715),
    (55.76996256764349, 37.36942982797446),
    (55.789736950483615, 37.3728868615282),
    (55.808798087528174, 37.388344151047676),
    (55.83260998737753, 37.39560097816893),
    (55.851747102850375, 37.39376480087579),
    (55.87090570963696, 37.41209100527676),
    (55.87659696295345, 37.42839459978549),
    (55.88161130650381, 37.445221243317135),
    (55.88711708090231, 37.482644383447834),
    (55.89207427475143, 37.49649435563702),
    (55.90782224163112, 37.54371914983502),
    (55.90978840669936, 37.58858112800599),
    (55.89518876022445, 37.67325996719509),
    (55.82959228057486, 37.82861019557688),
    (55.8822323534685, 37.72592724800108),
    (55.8138082895938, 37.83884777073161),
    (55.75481214376632, 37.84267307758329),
    (55.70418787329251, 37.8332852107992),
    (55.702989401989484, 37.83263932754),
    (55.65047653581307, 37.83493949978359),
    (55.64502320468091, 37.82690675054945),
    (55.62614603220174, 37.798215117726585),
    (55.59582667642601, 37.73945441049923),
    (55.587464115886156, 37.71946951925047),
    (55.58141301775248, 37.70325579370606),
    (55.57362538548569, 37.63521054231301),
    (55.57456040522403, 37.619314897938175),
    (55.58056831268785, 37.573856505131964),
    (55.58749528969654, 37.5451094875984),
    (55.593784581287494, 37.51884952838902),
    (55.60589190143268, 37.49776326563821),
    (55.61577037337298, 37.48617693805733),
    (55.62588555827154, 37.47443845687327),
    (55.63159809915896, 37.46778063484318),
    (55.65207693603693, 37.4436689941094),
    (55.65663799228618, 37.43816060545844),
    (55.66590855944432, 37.42912931533752),
    (55.68849971417, 37.4141437197791),
    (55.707656747292155, 37.39082356976081),
    (55.70992858606593, 37.38822422159842),
    (55.75188787932283, 37.366333001041205),
    (55.79604144033229, 37.37852370112031),
    (55.81331234523823, 37.38954092451),
    (55.81568484607161, 37.390191395766784),
    (55.82131114715086, 37.391900629017584),
    (55.825072975139875, 37.393084859162826),
    (55.830495842317646, 37.39451898008863),
    (55.8339338725267, 37.39594735722236),
    (55.85865656090271, 37.397073365517734),
    (55.86699779674642, 37.40492948497198),
    (55.87821893534327, 37.43308640028372),
    (55.88949415675149, 37.48972351315925),
    (55.90681458164319, 37.53369071576891),
    (55.910830265189425, 37.57059586873433),
    (55.911011046432726, 37.581529228009686),
    (55.89964948588706, 37.629701188337705),
    (55.895716922397085, 37.66346711671403),
    (55.89505379117015, 37.68453970149422),
    (55.894105661911894, 37.699083186567655),
    (55.89178148825972, 37.70718435431336),
    (55.87839320587734, 37.734177892950065),
    (55.82543390489343, 37.83464260085545),
    (55.81012946042399, 37.83951226232321),
    (55.80418173177062, 37.83998433110984),
    (55.802423269353746, 37.840209636667076),
    (55.90738403567146, 37.5979956303702),
]

MKAD_TREE = KDTree(MKAD_EXITS_COORDINATES)

KAD_CENTER = Coordinates(59.95, 30.305)


class DistanceCalculatorAbstract:
    def __init__(self, *, polygon: Polygon):
        self.polygon = polygon

    def get_distance(self, coordinates: Coordinates) -> int:
        """Returns distance from coordinates to polygon in kilometers."""
        if not self.polygon or geometry.is_inside_polygon(coordinates, self.polygon):
            return 0

        distance = self.calc_distance(coordinates)

        distance = round(float(distance) / 1000) if distance > 1000 else 1
        return distance

    def calc_distance(self, coordinates: Coordinates) -> float:
        """Caclulates distance from coordinates to polygon in meters using some strategy."""
        raise NotImplementedError


class NearestExitsGoogleDistanceCalculator(DistanceCalculatorAbstract):
    log_message = 'Рассчитано расстояние от ближайших выездов с полигона (в метрах)'

    def __init__(
            self,
            *,
            api: GoogleMapsApi,
            polygon: Polygon,
            exits_coordinates: List[PointTuple],
            exits_tree: Optional[KDTree] = None,
    ):
        super().__init__(polygon=polygon)
        self.api = api
        self.exits = exits_coordinates
        self.kdtree = exits_tree if exits_tree else KDTree(exits_coordinates)

    def calc_distance(self, coordinates: Coordinates) -> float:
        dists, indexes = self.kdtree.query((coordinates.latitude, coordinates.longitude), k=7)
        nearest_coordinates = list()
        for _, index in zip(dists, indexes):
            nearest_coordinates.append(self.exits[index])

        distance = float(self.api.get_distance_from_points(nearest_coordinates, coordinates.as_tuple()))
        logger.info(
            self.log_message,
            extra=dict(geo_distance=distance, geo_coordinates=coordinates.as_str())
        )
        return distance


class PolygonCenterGoogleDistanceCalculator(DistanceCalculatorAbstract):
    log_message = 'Рассчитано расстояние от центра полигона (в метрах)'

    def __init__(self, *, api: GoogleMapsApi, polygon: Polygon, center: Coordinates):
        super().__init__(polygon=polygon)
        self.api = api
        self.center = center

    def calc_distance(self, coordinates: Coordinates) -> float:
        driving_path = self.api.get_driving_path(self.center.as_tuple(), coordinates.as_tuple())
        distance = 0
        for step in reversed(driving_path):
            start_point = Coordinates(step['start_location']['lat'], step['start_location']['lng'])
            if geometry.is_inside_polygon(start_point, self.polygon):
                end_point = Coordinates(step['end_location']['lat'], step['end_location']['lng'])
                distance += geometry.get_part_outside_polygon(
                    geometry.get_line(start_point, end_point), self.polygon
                ) * step['distance']['value']
                break
            distance += step['distance']['value']
        logger.info(
            self.log_message,
            extra=dict(geo_distance=distance, geo_coordinates=coordinates.as_str())
        )
        return distance


class CachedDistanceCalculator(CacheableServiceAbstract, DistanceCalculatorAbstract):
    storage_class = CacheStorageDistance

    def refresh_value(self, key: Coordinates) -> int:
        return super().calc_distance(key)

    def calc_distance(self, coordinates: Coordinates) -> int:
        return self.get(coordinates)


class MkadDistanceCalculator(CachedDistanceCalculator, NearestExitsGoogleDistanceCalculator):
    expire_time = 60 * 60 * 24 * 30  # 30 days
    log_message = 'Рассчитано расстояние от МКАД (в метрах)'

    def __init__(self, storage, gmaps_client):
        super().__init__(
            storage=storage,
            api=GoogleMapsApi(gmaps_client),
            polygon=MKAD_POLYGON,
            exits_coordinates=MKAD_EXITS_COORDINATES,
            exits_tree=MKAD_TREE,
        )


class KadDistanceCalculator(CachedDistanceCalculator, PolygonCenterGoogleDistanceCalculator):
    expire_time = 60 * 60 * 24 * 30  # 30 days
    log_message = 'Рассчитано расстояние от КАД (в метрах)'

    def __init__(self, storage, gmaps_client):
        super().__init__(
            storage=storage,
            api=GoogleMapsApi(gmaps_client),
            polygon=KAD_POLYGON,
            center=KAD_CENTER
        )
