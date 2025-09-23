import collections
from typing import Any, Optional, Dict, List

from src.settings import quiply_settings

Cache = Dict[str, Any]


class StorageCache:
    _cache: Cache
    _max_size: int
    _hits: int
    _misses: int

    def __init__(self):
        self._config = quiply_settings.services.storage.cache
        self._cache: Cache = collections.OrderedDict()
        self._max_size = self._config.max_size
        self._hits = self._misses = 0

    def has(self, key: str) -> bool:
        if not self._config.enabled:
            return False
        return key in self._cache

    def get(self, key: str) -> Optional[Any]:
        if not self._config.enabled:
            return None
        try:
            value = self._cache.get(key)
            self._hits += 1
            return value
        except KeyError:
            self._misses += 1
            return None

    def try_get_prefetch(self, prefix: str) -> Optional[List[Any]]:
        if not self._config.enabled or not self._config.prefetch_templates:
            return None
        return self.get_all_with_prefix(prefix)

    def get_all_with_prefix(self, prefix: str) -> Optional[List[Any]]:
        if not self._config.enabled:
            return None
        values = []
        for key in self._cache.keys():
            if key.startswith(prefix):
                value = self._cache.get(key)
                self._cache[key] = value
                self._hits += 1
                values.append(value)
        if len(values) > 0:
            return values
        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        if not self._config.enabled:
            return
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self._max_size:
            first_key = next(iter(self._cache))
            self._cache.pop(first_key)
        self._cache[key] = value

    def set_many(self, items: Dict[str, Any]) -> None:
        if not self._config.enabled:
            return
        for key, value in items.items():
            self.set(key, value)

    def delete(self, key: str) -> None:
        if not self._config.enabled:
            return
        if key in self._cache:
            del self._cache[key]

    def stats(self) -> Dict[str, int]:
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
        }
