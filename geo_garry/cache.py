from typing import Any, Optional, Type


class CacheStorageNotFound(Exception):
    pass


class CacheValueNotFound(Exception):
    pass


class StorageInterface:
    def get(self, key):
        pass

    def set(self, key, value):
        pass

    def flushall(self):
        pass


class CacheStorageAbstract:
    expire_time = 60 * 60 * 24 * 30  # 30 days
    allow_empty = False

    def __init__(self, cache_storage):
        self.cache_storage = cache_storage

    def get_key(self, instance: Any) -> str:
        raise NotImplementedError

    def deserialize_value(self, value: bytes) -> Any:
        raise NotImplementedError

    def serialize_value(self, value: Any) -> str:
        raise NotImplementedError

    def get(self, instance: Any) -> Optional[Any]:
        key = self.get_key(instance)
        value = self.cache_storage.get(key)
        if not value:
            return None
        return self.deserialize_value(value)

    def set(self, instance: Any, value: Any) -> None:
        key = self.get_key(instance)
        self.cache_storage.set(key, self.serialize_value(value), ex=self.expire_time)


class CacheNullStorageAbstract(CacheStorageAbstract):  # pylint: disable=abstract-method
    allow_empty = True

    def get(self, instance: Any) -> Optional[Any]:
        key = self.get_key(instance)
        value = self.cache_storage.get(key)
        if not value and not self.cache_storage.exists(key):
            raise CacheValueNotFound()
        return self.deserialize_value(value)


class CacheableServiceAbstractMixin:
    def __init__(self, **kwargs):
        self.cache_storage: StorageInterface = kwargs.pop('storage')
        if not self.cache_storage:
            raise CacheStorageNotFound()
        super().__init__(**kwargs)

    storage_class: Type[CacheStorageAbstract]

    def refresh_value(self, key: Any) -> Any:
        raise NotImplementedError

    def get(self, key: Any) -> Any:
        storage = self.storage_class(self.cache_storage)

        try:
            cached_value = storage.get(key)
        except CacheValueNotFound:
            pass
        else:
            if cached_value or (not cached_value and storage.allow_empty):
                return cached_value

        refreshed_value = self.refresh_value(key)
        storage.set(key, refreshed_value)
        return refreshed_value
