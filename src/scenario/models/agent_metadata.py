from typing import Optional, List, Any

from pydantic import BaseModel, Field, ConfigDict

from src.framework.models import Message
from src.models import ScenarioInstance


class AgentMetadata(BaseModel):
    scenario_instance: ScenarioInstance
    user_message: Optional[Message] = Field(default=None)
    stack: List[Any] = Field(default_factory=list)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
