from typing import Optional, List, Dict, Literal

from pydantic import Field, ConfigDict

from ..base import SerializableObject
from .context import ContextReference
from .page_config import ScenarioPageConfig
from .page_field_config import ScenarioFieldConfig


class ScenarioConfig(SerializableObject):
    schema_id: str
    name: str
    user_id: str

    page_configs: List[ScenarioPageConfig] = Field(default_factory=list)

    difficulty: Optional[str] = Field(default=None)
    duration: Optional[str] = Field(default=None)

    scenario_additional_information: Optional[str] = Field(default=None)
    scenario_contexts: Optional[List[ContextReference]] = Field(default_factory=list[ContextReference])

    actor_ids: List[str] = Field(default_factory=list[str])
    actors_additional_information: Optional[Dict[str, str]] = Field(default_factory=dict[str, str])
    actors_contexts: Dict[str, List[ContextReference]] = Field(default_factory=dict[str, list[ContextReference]])

    special_actor_ids: Optional[List[str]] = Field(default_factory=list[str])

    user_additional_information: Optional[str] = Field(default=None)
    user_contexts: List[ContextReference] = Field(default_factory=list[ContextReference])

    debug_starting_conversation: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )

    def get_actor_additional_information(self, actor_id: str) -> str | None:
        if actor_id not in self.actors_additional_information:
            return None
        additional_information = self.actors_additional_information[actor_id]
        if additional_information is None or additional_information == '':
            return None
        return additional_information

    def get_actor_context(self, actor_id: str) -> List[ContextReference]:
        if actor_id not in self.actors_contexts:
            return []
        return self.actors_contexts[actor_id]

    def get_field_configs(self) -> Dict[str, Dict[str, ScenarioFieldConfig]]:
        field_configs = {}
        for page_config in self.page_configs:
            if page_config.template_type == 'fields':
                field_configs[page_config.template_uid] = page_config.get_field_config_dict()
        return field_configs
