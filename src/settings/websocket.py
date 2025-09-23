from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebSocketSettings(BaseSettings):
    accept_timeout: int = Field(default=10)
    ready_event_timeout: int = Field(default=30)
