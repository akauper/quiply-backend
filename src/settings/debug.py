from typing import Optional, TypeVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseScenarioDebugSettings(BaseSettings):
    enabled: bool = Field(default=False)


TDebugSettings = TypeVar('TDebugSettings', bound=BaseScenarioDebugSettings)


class ConversationDebugSettings(BaseScenarioDebugSettings):
    pass


class DebateDebugSettings(BaseScenarioDebugSettings):
    use_pregenerated_opinion: bool = Field(default=False)


class InterviewDebugSettings(BaseScenarioDebugSettings):
    pass


class SpeedDatingDebugSettings(BaseScenarioDebugSettings):
    pass


class DebugSettings(BaseSettings):
    enabled: bool = Field(default=False)
    force_user_id: Optional[str] = Field(default=None)

    use_pregenerated_personality: bool = Field(default=False)
    use_pregenerated_stages: bool = Field(default=False)
    use_pregenerated_conversations: bool = Field(default=False)

    conversation: ConversationDebugSettings = Field(default_factory=ConversationDebugSettings)
    debate: DebateDebugSettings = Field(default_factory=DebateDebugSettings)
    interview: InterviewDebugSettings = Field(default_factory=InterviewDebugSettings)
    speed_dating: SpeedDatingDebugSettings = Field(default_factory=SpeedDatingDebugSettings)

    model_config = SettingsConfigDict(extra='allow')
