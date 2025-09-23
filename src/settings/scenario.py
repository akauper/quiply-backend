from typing import List, TYPE_CHECKING, Any

from pydantic import Field
from pydantic_settings import BaseSettings

from .logging import BaseLoggingSettings

# if TYPE_CHECKING:
#     from ..framework.evaluation.callback import BaseAsyncCallback


class ScenarioLoggingSettings(BaseLoggingSettings):
    stage_log_level: str = Field(default='INFO')
    llm_log_level: str = Field(default='INFO')
    websocket_log_level: str = Field(default='INFO')


class ScenarioSettings(BaseSettings):
    logging: ScenarioLoggingSettings = Field(default_factory=ScenarioLoggingSettings)

    message_mode: str = Field(default='stream')
    max_conversation_tokens: int = Field(default=-1)
    agent_callbacks: List[Any] = Field(default_factory=list)

    def initialize_dependencies(self):
        if self.allow_stt:
            pass

    def update_from(self, other: dict):
        for key, value in other.items():
            if hasattr(self, key):
                setattr(self, key, value)
