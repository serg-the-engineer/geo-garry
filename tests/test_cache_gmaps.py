from unittest import mock

from geo_garry.cache import CacheableServiceAbstract
from geo_garry.dataclasses import Coordinates, CoordinatesAddress
from geo_garry.gmaps.cache import CacheStorageCoordinates, CacheStorageAddress


def test_cache_storage_coordinates():
    refresh_mock = mock.Mock(name='refresh')
    get_mock = mock.Mock(name='get')
    set_mock = mock.Mock(name='set')
    exists_mock = mock.Mock(name='exists')

    def reset_mocks():
        refresh_mock.reset_mock()
        get_mock.reset_mock()
        set_mock.reset_mock()

    class TestService(CacheableServiceAbstract):
        storage_class = CacheStorageCoordinates

        def refresh_value(self, key):
            return refresh_mock(key)

    service = TestService(
        storage=mock.Mock(
            get=get_mock,
            set=set_mock,
            exists=exists_mock,
        )
    )

    get_mock.return_value = None
    exists_mock.return_value = False
    refresh_mock.return_value = Coordinates(1, 2)

    assert service.get('address1') == Coordinates(1, 2)
    get_mock.assert_called_once_with('coordinates:address1')
    refresh_mock.assert_called_once_with('address1')
    set_mock.assert_called_once_with('coordinates:address1', '1,2', ex=2592000)

    reset_mocks()
    get_mock.return_value = None
    exists_mock.return_value = True
    assert service.get('address1') is None
    refresh_mock.assert_not_called()
    set_mock.assert_not_called()

    get_mock.return_value = b'1,2'
    assert service.get('address1') == Coordinates(1, 2)
    refresh_mock.assert_not_called()
    set_mock.assert_not_called()


def test_cache_storage_address():
    refresh_mock = mock.Mock(name='refresh')
    get_mock = mock.Mock(name='get')
    set_mock = mock.Mock(name='set')
    exists_mock = mock.Mock(name='exists')

    def reset_mocks():
        refresh_mock.reset_mock()
        get_mock.reset_mock()
        set_mock.reset_mock()

    class TestService(CacheableServiceAbstract):
        storage_class = CacheStorageAddress

        def refresh_value(self, key):
            return refresh_mock(key)

    service = TestService(
        storage=mock.Mock(
            get=get_mock,
            set=set_mock,
            exists=exists_mock,
        )
    )

    get_mock.return_value = None
    exists_mock.return_value = False
    refresh_mock.return_value = CoordinatesAddress(1, 2, 'address2')

    assert service.get(Coordinates(1, 2)) == CoordinatesAddress(1, 2, 'address2')
    get_mock.assert_called_once_with('geo:1,2')
    refresh_mock.assert_called_once_with(Coordinates(1, 2))
    set_mock.assert_called_once_with('geo:1,2', '1,2;address2;;', ex=2592000)

    reset_mocks()
    get_mock.return_value = b'5,7;address2;;1'
    assert service.get(Coordinates(1, 2)) == CoordinatesAddress(5, 7, 'address2', None, 1)
    refresh_mock.assert_not_called()
    set_mock.assert_not_called()
