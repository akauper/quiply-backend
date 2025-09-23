from typing import List

from pydantic import Field, BaseModel

from ...base import BaseAutomationConfig
from src.framework import BaseAsyncCallback


class AutoScenarioConfig(BaseAutomationConfig):
    auto_user_schema_id: str = Field(default='frank')

    scenario_schema_id: str = Field(default="pitch_to_investors")
    scenario_name: str = Field(default="Pitch To Investors")
    field_values: dict = Field(
        default={"audience_type": "investor", "audience_inclination": "neutral"}
    )
    difficulty: str = Field(default="easy")
    duration: str = Field(default="short")

    actor_ids: list = Field(default=["sue"])

    agent_callbacks: List[BaseAsyncCallback] = Field(default_factory=list)
