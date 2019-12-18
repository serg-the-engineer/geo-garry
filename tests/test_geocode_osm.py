from unittest import mock

from geo_garry import geocode, Coordinates
from geo_garry.osm import OpenStreetMapsAddress, OSM_ADDRESS_SCHEMAS


OSM_RESPONSES = [
    {
        "place_id":"199296695",
        "licence":"Data © OpenStreetMap contributors",
        "osm_type":"relation",
        "osm_id":"7883120",
        "lat":"55.7483792",
        "lon":"37.5420856941404",
        "place_rank":"30",
        "category":"building",
        "type":"yes",
        "importance":"0.213327567897527",
        "addresstype":"building",
        "name":"Башня Эволюция",
        "display_name":"Башня Эволюция, 4 с2, РФ",
        "address":{
            "building":"Башня Эволюция",
            "house_number":"4 с2",
            "road":"Пресненская набережная",
            "suburb":"Пресненский район",
            "state_district":"Центральный административный округ",
            "state":"Москва",
            "postcode":"123317",
            "country":"РФ",
            "country_code":"ru"
        },
    },
    {
        "place_id":"96435798",
        "licence":"Data © OpenStreetMap contributors",
        "osm_type":"way",
        "osm_id":"90983917",
        "lat":"44.60916135",
        "lon":"33.5259145492637",
        "place_rank":"30",
        "category":"building",
        "type":"yes",
        "importance":"0",
        "addresstype":"building",
        "name":None,
        "display_name":"33Б, Севастополь, 299000-299699, Украина",
        "address":{
            "house_number":"33Б",
            "road":"Луначарского улица",
            "city":"Севастополь",
            "state_district":"Ленинский район",
            "state":"Севастополь",
            "postcode":"299000-299699",
            "country":"Украина",
            "country_code":"ua"
        },
    },
    {
        "place_id":"116817872",
        "licence":"Data © OpenStreetMap contributors",
        "osm_type":"way",
        "osm_id":"173498298",
        "lat":"45.6205207",
        "lon":"63.2727836187316",
        "place_rank":"30",
        "category":"building",
        "type":"yes",
        "importance":"0",
        "addresstype":"building",
        "name":"Больница Акай",
        "display_name":"Больница Акай, ... Казахстан",
        "address":{
            "building":"Больница Акай",
            "road":"улица Гагарина",
            "village":"Ахай",
            "county":"Байконыр Г.А.",
            "state":"Кызылординская область",
            "postcode":"468320",
            "country":"Казахстан",
            "country_code":"kz"
        },
    }
]


def test_osm_address():

    address = OpenStreetMapsAddress(OSM_RESPONSES[0])
    assert address.format() == 'Москва, Пресненская набережная, Башня Эволюция, 4 с2'
    assert address.format(terms_schema=OSM_ADDRESS_SCHEMAS['federal_subject']) == 'Москва'

    address = OpenStreetMapsAddress(OSM_RESPONSES[1])
    assert address.format() == 'Севастополь, Луначарского улица, 33Б'
    assert address.format(terms_schema=OSM_ADDRESS_SCHEMAS['federal_subject']) == 'Севастополь'

    address = OpenStreetMapsAddress(OSM_RESPONSES[2])
    assert address.format() == 'Байконур, улица Гагарина, Больница Акай'
    assert address.format(terms_schema=OSM_ADDRESS_SCHEMAS['federal_subject']) == 'Байконур'


@mock.patch('geo_garry.osm.requests.get')
def test_osm_geocoder_address(api_mock):
    geocoder = geocode.OpenStreetMapsGeocoder()
    response = mock.Mock(json=mock.Mock(return_value=OSM_RESPONSES[1]))
    api_mock.return_value = response
    result = geocoder.get_address(Coordinates(123, 123))
    assert result == 'Севастополь, Луначарского улица, 33Б'
    api_mock.assert_called_once_with(
        "https://nominatim.openstreetmap.org/reverse/",
        params={
            "format": "jsonv2",
            "lat": 123,
            "lon": 123,
            "accept-language": "ru",
        }
    )


@mock.patch('geo_garry.osm.requests.get')
def test_osm_geocoder_federal(api_mock):
    geocoder = geocode.OpenStreetMapsGeocoder()
    response = mock.Mock(json=mock.Mock(return_value=OSM_RESPONSES[2]))
    api_mock.return_value = response
    result = geocoder.get_federal_code(Coordinates(123, 123))
    assert result == 99
    api_mock.assert_called_once_with(
        "https://nominatim.openstreetmap.org/reverse/",
        params={
            "format": "jsonv2",
            "lat": 123,
            "lon": 123,
            "accept-language": "ru",
        }
    )
