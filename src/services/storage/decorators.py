from functools import wraps
from typing import Callable


def cacheable(cache_key_prefix: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_key = f"{cache_key_prefix}:{args}"

            if self._config.cache.enabled:
                cached_value = self._cache.get(cache_key)
                if cached_value is not None:
                    return cached_value

            result = func(self, *args, **kwargs)

            if self._config.cache.enabled:
                self._cache.set(cache_key, result)

            return result

        return wrapper

    return decorator
