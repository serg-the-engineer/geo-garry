from unittest import mock

from geo_garry import geocode
from geo_garry.gmaps.api import GoogleMapsAddress, GOOGLE_MAPS_ADDRESS_SCHEMAS
from geo_garry.dataclasses import Coordinates, CoordinatesWithCity


def test_google_maps_address():
    terms_1 = [
        {'long_name': '9а',
         'short_name': '9а',
         'types': ['street_number']},
        {'long_name': 'улица Профессора Качалова',
         'short_name': 'ул. Профессора Качалова',
         'types': ['route']},
        {'long_name': 'Санкт-Петербург',
         'short_name': 'СПБ',
         'types': ['locality', 'political']},
        {'long_name': 'Невский',
         'short_name': 'Невский',
         'types': ['administrative_area_level_3', 'political']},
        {'long_name': 'Санкт-Петербург',
         'short_name': 'Санкт-Петербург',
         'types': ['administrative_area_level_2', 'political']},
        {'long_name': 'Россия',
         'short_name': 'RU',
         'types': ['country', 'political']},
        {'long_name': '192019', 'short_name': '192019', 'types': ['postal_code']}
    ]
    addr = GoogleMapsAddress(terms_1)
    assert addr.format() == 'Санкт-Петербург, улица Профессора Качалова, 9а'
    assert addr.format(GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']) == 'Санкт-Петербург'

    terms_2 = [
        {'long_name': 'владение 14',
         'short_name': 'владение 14',
         'types': ['street_number']},
        {'long_name': 'МКАД 87 километр (внутр.)',
         'short_name': 'МКАД 87 км (внутр.)',
         'types': ['route']},
        {'long_name': 'Северо-Восточный административный округ',
         'short_name': 'Северо-Восточный административный округ',
         'types': ['political', 'sublocality', 'sublocality_level_1']},
        {'long_name': 'Бибирево',
         'short_name': 'Бибирево',
         'types': ['administrative_area_level_3', 'political']},
        {'long_name': 'Москва',
         'short_name': 'Москва',
         'types': ['administrative_area_level_2', 'political']},
        {'long_name': 'Россия',
         'short_name': 'RU',
         'types': ['country', 'political']},
        {'long_name': '127543', 'short_name': '127543', 'types': ['postal_code']}
    ]
    addr = GoogleMapsAddress(terms_2)
    assert addr.format() == \
        'Москва, Бибирево, МКАД 87 километр (внутр.), владение 14'
    assert addr.format(GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']) == 'Москва'

    terms_3 = [
        {'long_name': '39',
         'short_name': '39',
         'types': ['street_number']},
        {'long_name': 'Волковское шоссе',
         'short_name': 'Волковское ш.',
         'types': ['route']},
        {'long_name': 'Мытищи',
         'short_name': 'Мытищи',
         'types': ['locality', 'political']},
        {'long_name': 'город Мытищи',
         'short_name': 'город Мытищи',
         'types': ['administrative_area_level_2', 'political']},
        {'long_name': 'Московская область',
         'short_name': 'МО',
         'types': ['administrative_area_level_1', 'political']},
        {'long_name': 'Россия',
         'short_name': 'RU',
         'types': ['country', 'political']},
        {'long_name': '141021', 'short_name': '141021', 'types': ['postal_code']}
    ]
    addr = GoogleMapsAddress(terms_3)
    assert addr.format() == \
        'Мытищи, Волковское шоссе, 39'
    assert addr.format(GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']) == 'Московская область'

    terms_4 = [
        {'long_name': 'Сельхозтехника',
         'short_name': 'Сельхозтехника',
         'types': ['bus_station', 'establishment', 'point_of_interest', 'transit_station']},
        {'long_name': 'Челюскинский',
         'short_name': 'Челюскинский',
         'types': ['locality', 'political']},
        {'long_name': 'Пушкинский район',
         'short_name': 'Пушкинский р-н',
         'types': ['administrative_area_level_2', 'political']},
        {'long_name': 'Московская область',
         'short_name': 'МО',
         'types': ['administrative_area_level_1', 'political']},
        {'long_name': 'Россия',
         'short_name': 'RU',
         'types': ['country', 'political']},
        {'long_name': '141220', 'short_name': '141220', 'types': ['postal_code']}
    ]
    addr = GoogleMapsAddress(terms_4)
    assert addr.format() == \
        'Челюскинский, ост. Сельхозтехника'
    assert addr.format(GOOGLE_MAPS_ADDRESS_SCHEMAS['federal_subject']) == 'Московская область'



@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_gmaps_forward_geocode(api_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=b'1.22339,4.56561'))
    service = geocode.GmapsCacheableGeocodeService(storage=storage_mock, api=api_mock)
    assert service.get('Moscow City') == Coordinates(1.22339, 4.56561)

    api_mock.get_coordinates.assert_not_called()
    api_mock.get_coordinates.return_value = (1.22339, 4.56561)
    storage_mock = mock.Mock(get=mock.Mock(return_value=None), exists=mock.Mock(return_value=True))
    service = geocode.GmapsCacheableGeocodeService(storage=storage_mock, api=api_mock)
    assert service.get('Moscow City') is None

    storage_mock = mock.Mock(get=mock.Mock(return_value=None), exists=mock.Mock(return_value=False))
    service = geocode.GmapsCacheableGeocodeService(storage=storage_mock, api=api_mock)
    assert service.get('Moscow City') == Coordinates(1.22339, 4.56561)
    api_mock.get_coordinates.assert_called_once_with('Moscow City')
    storage_mock.set.assert_called_once_with('coordinates:Moscow City', '1.22339,4.56561', ex=60*60*24*30)
    storage_mock.get.assert_called_once_with('coordinates:Moscow City')


@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_gmaps_reverse_geocode(api_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=b'address'))
    service = geocode.GmapsCacheableReverseGeocodeService(storage=storage_mock, api=api_mock)
    assert service.get(Coordinates(1.22339, 4.56561)) == 'address'

    api_mock.get_address_components.assert_not_called()
    api_mock.get_address_components.return_value = [
        {'long_name': '9а',
         'short_name': '9а',
         'types': ['street_number']},
        {'long_name': 'улица Профессора Качалова',
         'short_name': 'ул. Профессора Качалова',
         'types': ['route']},
        {'long_name': 'Санкт-Петербург',
         'short_name': 'СПБ',
         'types': ['locality', 'political']},
    ]
    addr = 'Санкт-Петербург, улица Профессора Качалова, 9а'
    storage_mock = mock.Mock(get=mock.Mock(return_value=None))
    service = geocode.GmapsCacheableReverseGeocodeService(storage=storage_mock, api=api_mock)
    assert service.get(Coordinates(1.22339, 4.56561)) == addr
    api_mock.get_address_components.assert_called_once_with((1.22339, 4.56561))
    storage_mock.set.assert_called_once_with('address:1.2234,4.5656', addr, ex=60*60*24*30)
    storage_mock.get.assert_called_once_with('address:1.2234,4.5656')


@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_gmaps_reverse_federal_geocode(api_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=b'address'))
    service = geocode.GmapsCacheableFederalSubjectService(storage=storage_mock, api=api_mock)
    assert service.get(Coordinates(1.22339, 4.56561)) == 'address'

    api_mock.get_address_components.assert_not_called()
    api_mock.get_address_components.return_value = [
        {'long_name': '9а',
         'short_name': '9а',
         'types': ['street_number']},
        {'long_name': 'улица Профессора Качалова',
         'short_name': 'ул. Профессора Качалова',
         'types': ['route']},
        {'long_name': 'Санкт-Петербург',
         'short_name': 'СПБ',
         'types': ['locality', 'political']},
        {'long_name': 'Санкт-Петербург',
         'short_name': 'Санкт-Петербург',
         'types': ['administrative_area_level_2', 'political']},
        {'long_name': 'Россия',
         'short_name': 'RU',
         'types': ['country', 'political']},
    ]
    addr = 'Санкт-Петербург'
    storage_mock = mock.Mock(get=mock.Mock(return_value=None))
    service = geocode.GmapsCacheableFederalSubjectService(storage=storage_mock, api=api_mock)
    assert service.get(Coordinates(1.22339, 4.56561)) == addr
    api_mock.get_address_components.assert_called_once_with((1.22339, 4.56561))
    storage_mock.set.assert_called_once_with('federal:1.2234,4.5656', addr, ex=60*60*24*30)
    storage_mock.get.assert_called_once_with('federal:1.2234,4.5656')


@mock.patch('geo_garry.gmaps.api.GoogleMapsApi')
def test_gmaps_geocode_with_geo(api_mock):
    storage_mock = mock.Mock(get=mock.Mock(return_value=b'1,2;address'))
    service = geocode.GmapsCacheableCoordinatesWithGeoService(storage=storage_mock, api=api_mock)
    assert service.get_coordinates_with_city('Уруру') == CoordinatesWithCity(1, 2, 'address')

    api_mock.get_coordinates_and_address_components.assert_not_called()
    api_mock.get_coordinates_and_address_components.return_value = {
        'coordinates': (100, 200),
        'address_components': [
            {'long_name': '9а',
             'short_name': '9а',
             'types': ['street_number']},
            {'long_name': 'улица Профессора Качалова',
             'short_name': 'ул. Профессора Качалова',
             'types': ['route']},
            {'long_name': 'Санкт-Петербург',
             'short_name': 'СПБ',
             'types': ['locality', 'political']},
            {'long_name': 'Санкт-Петербург',
             'short_name': 'Санкт-Петербург',
             'types': ['administrative_area_level_2', 'political']},
            {'long_name': 'Россия',
             'short_name': 'RU',
             'types': ['country', 'political']},
        ],
    }
    storage_mock = mock.Mock(get=mock.Mock(return_value=None), exists=mock.Mock(return_value=True))
    service = geocode.GmapsCacheableCoordinatesWithGeoService(storage=storage_mock, api=api_mock)
    assert service.get_coordinates_with_city('Assa') is None
    storage_mock.get.assert_called_once_with('address_geo:Assa')
    storage_mock.reset_mock()

    storage_mock.exists = mock.Mock(return_value=False)
    assert service.get_coordinates_with_city('Assa') == CoordinatesWithCity(100, 200, 'Санкт-Петербург')
    api_mock.get_coordinates_and_address_components.assert_called_once_with('Assa')
    storage_mock.set.assert_called_once_with(
        'address_geo:Assa', '100,200;Санкт-Петербург', ex=60*60*24*30,
    )
    storage_mock.get.assert_called_once_with('address_geo:Assa')
