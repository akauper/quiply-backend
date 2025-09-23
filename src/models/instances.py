from typing import Any, Optional

from pydantic import Field, ConfigDict

from .user.account_data import AccountData
from .base import SerializableObject
from .configs import ScenarioConfig


class ScenarioInstance(SerializableObject):
    account_data: AccountData
    scenario_config: ScenarioConfig

    llm_completion_info: Optional[Any] = Field(default=None)

    model_config = ConfigDict(
        extra='allow',
        from_attributes=True
    )

    @property
    def schema_id(self):
        return self.scenario_config.schema_id

    @property
    def user_id(self):
        return self.account_data.id
