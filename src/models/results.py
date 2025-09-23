from typing import List, Optional, Any

from pydantic import Field, ConfigDict

from .analysis import ScenarioAnalysis
from .base import SerializableObject
from .instances import ScenarioInstance
from src.framework import Conversation


class ScenarioResult(SerializableObject):
    scenario_instance: ScenarioInstance = Field(default_factory=dict)

    conversations: List[Conversation] = Field(default_factory=list[Conversation])
    analysis: ScenarioAnalysis = Field(default=dict)
    total_completion_info: Optional[Any] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )
