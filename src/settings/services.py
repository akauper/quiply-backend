from enum import Enum
from typing import ClassVar

from pydantic import Field
from pydantic.v1 import validator
from pydantic_settings import BaseSettings


class LanguageModelQuality(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class ServiceConfig(BaseSettings):
    enabled: bool = Field(default=True)
    provider: str


class CacheConfig(BaseSettings):
    enabled: bool = Field(default=True)
    prefetch_templates: bool = Field(default=True)
    max_size: int = Field(default=10_000)


class StorageConfig(ServiceConfig):
    provider: str = Field(default='firestore')
    cache: CacheConfig = Field(default_factory=CacheConfig)
    app_package_update_interval: int = Field(default=5)


class ServicesSettings(BaseSettings):
    storage: StorageConfig = Field(default_factory=StorageConfig)