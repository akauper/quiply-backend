from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FastAPISettings(BaseSettings):
    title: str = 'Quiply API'
    version: int = 1
    docs_url: str = '/docs'
    redoc_url: str = '/redoc'
    contact: Dict[str, str] = Field(
        default={
            'name': 'Quiply',
            'url': 'https://quiply.ai',
            'email': 'support@quiply.ai'
        }
    )

    cors_origins: list[str] = ["*"]
    cors_origins_regex: str | None = None
    cors_methods: list[str] = ['*']
    cors_headers: list[str] = ['*']

    allow_registration: bool = True

    # model_config = SettingsConfigDict(env_prefix='FASTAPI_', env_file='.env')

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            'title': self.title,
            'version': self.version,
            'docs_url': self.docs_url,
            'redoc_url': self.redoc_url,
            'contact': self.contact,
        }
