from unittest import mock

from geo_garry import distance, Coordinates


def test_distance_calculator():
    service = distance.DistanceCalculatorAbstract(polygon=distance.MKAD_EXITS_POLYGON)

    with mock.patch.object(service, 'calc_distance', return_value=100500) as calc_mock:
        inside_mkad = Coordinates(latitude=55.6892209716432, longitude=37.752854389528585)
        assert service.get_distance(inside_mkad) == 0
        calc_mock.assert_not_called()

    with mock.patch.object(service, 'calc_distance', return_value=100590.1234) as calc_mock:
        outside_mkad = Coordinates(latitude=50.4254225, longitude=36.9020654)
        assert service.get_distance(outside_mkad) == 101
        calc_mock.assert_called_once_with(outside_mkad)

    with mock.patch.object(service, 'calc_distance', return_value=63) as calc_mock:
        outside_mkad = Coordinates(latitude=50.4254225, longitude=36.9020654)
        assert service.get_distance(outside_mkad) == 1
        calc_mock.assert_called_once_with(outside_mkad)


@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_nearest_exits_calculator(api_mock):
    api_mock.get_distance_from_points.return_value = 5900

    service = distance.NearestExitsGoogleDistanceCalculator(
        api=api_mock,
        polygon=distance.MKAD_EXITS_POLYGON,
        exits_coordinates=distance.MKAD_EXITS_COORDINATES,
        exits_tree=distance.MKAD_TREE,
    )

    coords = Coordinates(123.10, 123.10)
    assert service.calc_distance(coords) == 5900
    api_mock.get_distance_from_points.assert_called_once_with([
        (55.82543390489343, 37.83464260085545),
        (55.82959228057486, 37.82861019557688),
        (55.8138082895938, 37.83884777073161),
        (55.81012946042399, 37.83951226232321),
        (55.80418173177062, 37.83998433110984),
        (55.802423269353746, 37.840209636667076),
        (55.77682626803085, 37.84269989967345)
    ], (123.10, 123.10))
    api_mock.get_distance_from_points.reset_mock()
    coords = Coordinates(153.10, 173.10)
    service.calc_distance(coords)
    api_mock.get_distance_from_points.assert_called_once_with([
        (55.82543390489343, 37.83464260085545),
        (55.82959228057486, 37.82861019557688),
        (55.8138082895938, 37.83884777073161),
        (55.81012946042399, 37.83951226232321),
        (55.80418173177062, 37.83998433110984),
        (55.802423269353746, 37.840209636667076),
        (55.77682626803085, 37.84269989967345)
    ], (153.10, 173.10))


@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_polygon_center(api_mock):
    api_mock.get_driving_path.return_value = [
        {'distance': {'text': '68 m', 'value': 68},
         'duration': {'text': '1 min', 'value': 12},
         'end_location': {'lat': 59.9494407, 'lng': 30.3051397},
         'start_location': {'lat': 59.950025, 'lng': 30.3049966},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.9 km', 'value': 911},
         'duration': {'text': '3 mins', 'value': 181},
         'end_location': {'lat': 59.95240949999999, 'lng': 30.2904161},
         'start_location': {'lat': 59.9494407, 'lng': 30.3051397},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.3 km', 'value': 256},
         'duration': {'text': '1 min', 'value': 48},
         'end_location': {'lat': 59.95395199999999, 'lng': 30.2870172},
         'start_location': {'lat': 59.95240949999999, 'lng': 30.2904161},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '1.2 km', 'value': 1171},
         'duration': {'text': '2 mins', 'value': 97},
         'end_location': {'lat': 59.96126159999999, 'lng': 30.2720644},
         'start_location': {'lat': 59.95395199999999, 'lng': 30.2870172},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '1.1 km', 'value': 1128},
         'duration': {'text': '2 mins', 'value': 92},
         'end_location': {'lat': 59.9529837, 'lng': 30.2661487},
         'start_location': {'lat': 59.96126159999999, 'lng': 30.2720644},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.2 km', 'value': 155},
         'duration': {'text': '1 min', 'value': 34},
         'end_location': {'lat': 59.9539901, 'lng': 30.266071},
         'start_location': {'lat': 59.9529837, 'lng': 30.2661487},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '2.6 km', 'value': 2633},
         'duration': {'text': '2 mins', 'value': 145},
         'end_location': {'lat': 59.9618416, 'lng': 30.2237484},
         'start_location': {'lat': 59.9539901, 'lng': 30.266071},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '14.2 km', 'value': 14150},
         'duration': {'text': '9 mins', 'value': 535},
         'end_location': {'lat': 60.0594314, 'lng': 30.1433647},
         'start_location': {'lat': 59.9618416, 'lng': 30.2237484},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.9 km', 'value': 888},
         'duration': {'text': '1 min', 'value': 59},
         'end_location': {'lat': 60.05786469999999, 'lng': 30.1353269},
         'start_location': {'lat': 60.0594314, 'lng': 30.1433647},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '23.9 km', 'value': 23930},
         'duration': {'text': '14 mins', 'value': 843},
         'end_location': {'lat': 60.0135102, 'lng': 29.71841319999999},
         'start_location': {'lat': 60.05786469999999, 'lng': 30.1353269},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.3 km', 'value': 283},
         'duration': {'text': '1 min', 'value': 22},
         'end_location': {'lat': 60.01416589999999, 'lng': 29.7167109},
         'start_location': {'lat': 60.0135102, 'lng': 29.71841319999999},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '3.0 km', 'value': 3017},
         'duration': {'text': '4 mins', 'value': 253},
         'end_location': {'lat': 60.0012631, 'lng': 29.762545},
         'start_location': {'lat': 60.01416589999999, 'lng': 29.7167109},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.4 km', 'value': 388},
         'duration': {'text': '1 min', 'value': 40},
         'end_location': {'lat': 59.9980647, 'lng': 29.7597875},
         'start_location': {'lat': 60.0012631, 'lng': 29.762545},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '0.4 km', 'value': 382},
         'duration': {'text': '1 min', 'value': 70},
         'end_location': {'lat': 59.9966984, 'lng': 29.7660179},
         'start_location': {'lat': 59.9980647, 'lng': 29.7597875},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '88 m', 'value': 88},
         'duration': {'text': '1 min', 'value': 19},
         'end_location': {'lat': 59.9959712, 'lng': 29.7653955},
         'start_location': {'lat': 59.9966984, 'lng': 29.7660179},
         'travel_mode': 'DRIVING'},
        {'distance': {'text': '9 m', 'value': 9},
         'duration': {'text': '1 min', 'value': 2},
         'end_location': {'lat': 59.9959303, 'lng': 29.7655452},
         'start_location': {'lat': 59.9959712, 'lng': 29.7653955},
         'travel_mode': 'DRIVING'},
    ]
    service = distance.PolygonCenterGoogleDistanceCalculator(
        api=api_mock,
        polygon=distance.KAD_POLYGON,
        center=distance.KAD_CENTER,
    )
    assert round(service.calc_distance(
        Coordinates(latitude=59.991988, longitude=29.775469),
    )) == 35823
    api_mock.get_driving_path.assert_called_once_with(distance.KAD_CENTER.as_tuple(), (59.991988, 29.775469))


@mock.patch('geo_garry.distance.DistanceCalculatorAbstract.calc_distance')
def test_cacheable_calculator(calc_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=12345))
    service = distance.CachedDistanceCalculator(storage=storage_mock, polygon=distance.MKAD_EXITS_POLYGON)
    outside_mkad = Coordinates(latitude=50.4254225, longitude=36.9020654)
    assert service.get_distance(outside_mkad) == 12
    storage_mock.get.assert_called_once_with('distance:50.4254225,36.9020654')
    calc_mock.assert_not_called()

    calc_mock.return_value = 12345
    storage_mock = mock.Mock(get=mock.Mock(return_value=None))
    service = distance.CachedDistanceCalculator(storage=storage_mock, polygon=distance.MKAD_EXITS_POLYGON)
    assert service.get_distance(outside_mkad) == 12
    storage_mock.set.assert_called_once_with('distance:50.4254225,36.9020654', '12345', ex=60*60*24*30)
    calc_mock.assert_called_once_with(outside_mkad)


@mock.patch('geo_garry.distance.NearestExitsGoogleDistanceCalculator.calc_distance')
def test_mkad_calculator(calc_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=12345))
    service = distance.MkadDistanceCalculator(storage=storage_mock, gmaps_client=mock.Mock())
    outside_mkad = Coordinates(latitude=50.4254225, longitude=36.9020654)
    assert service.get_distance(outside_mkad) == 12
    storage_mock.get.assert_called_once_with('distance:50.4254225,36.9020654')
    calc_mock.assert_not_called()

    calc_mock.return_value = 12345
    storage_mock = mock.Mock(get=mock.Mock(return_value=None))
    service = distance.MkadDistanceCalculator(storage=storage_mock, gmaps_client=mock.Mock())
    assert service.get_distance(outside_mkad) == 12
    storage_mock.set.assert_called_once_with('distance:50.4254225,36.9020654', '12345', ex=60*60*24*30)
    calc_mock.assert_called_once_with(outside_mkad)


@mock.patch('geo_garry.distance.PolygonCenterGoogleDistanceCalculator.calc_distance')
def test_kad_calculator(calc_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=12345))
    service = distance.KadDistanceCalculator(storage=storage_mock, gmaps_client=mock.Mock())
    outside_kad = Coordinates(latitude=59.991988, longitude=29.775469)
    assert service.get_distance(outside_kad) == 12
    storage_mock.get.assert_called_once_with('distance:59.991988,29.775469')
    calc_mock.assert_not_called()

    calc_mock.return_value = 12345
    storage_mock = mock.Mock(get=mock.Mock(return_value=None))
    service = distance.KadDistanceCalculator(storage=storage_mock, gmaps_client=mock.Mock())
    assert service.get_distance(outside_kad) == 12
    storage_mock.set.assert_called_once_with('distance:59.991988,29.775469', '12345', ex=60*60*24*30)
    calc_mock.assert_called_once_with(outside_kad)
