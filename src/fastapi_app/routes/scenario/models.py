from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.models import ScenarioConfig


class OverrideScenarioSettings(BaseModel):
    message_mode: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )


class CreateScenarioRequest(BaseModel):
    user_id: str
    scenario_config: ScenarioConfig
    overrideSettings: Optional[OverrideScenarioSettings] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )


class EndScenarioRequest(BaseModel):
    user_id: str
    scenario_instance_id: str

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )
