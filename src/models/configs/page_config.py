from typing import List, Optional, Dict, Union

from pydantic import BaseModel, Field

from src.models.schemas.scenario import ScenarioSchema
from ..schemas.scenario.page_schema import PageSchemaType, PageSchema
from .page_field_config import ScenarioFieldConfig


class ScenarioPageConfigBase(BaseModel):
    page_schema_type: PageSchemaType
    page_schema_uid: str

    def get_page_template(self, scenario_schema: ScenarioSchema) -> PageSchema:
        for page_schema in scenario_schema.pages:
            if page_schema.uid == self.page_schema_uid:
                return page_schema
        raise ValueError(f'Page schema not found: {self.page_schema_uid}')


class ScenarioPageConfigFields(ScenarioPageConfigBase):
    page_schema_type: PageSchemaType = PageSchemaType.FIELDS
    page_schema_uid: str = 'fields'
    field_configs: List[ScenarioFieldConfig] = Field(default_factory=list[ScenarioFieldConfig])

    def get_field_config_dict(self) -> Dict[str, ScenarioFieldConfig]:
        return {field_config.field_schema_uid: field_config for field_config in self.field_configs}


class ScenarioPageConfigActorSelection(ScenarioPageConfigBase):
    page_schema_type: PageSchemaType = PageSchemaType.ACTOR_SELECTION
    page_schema_uid: str = 'actor_selection'
    actor_ids: List[str] = Field(default_factory=list[str])
    actors_additional_information: Optional[Dict[str, str]] = Field(default_factory=dict[str, str])


ScenarioPageConfig = Union[
    ScenarioPageConfigFields,
    ScenarioPageConfigActorSelection
]

ScenarioPageConfigFields.model_rebuild()
ScenarioPageConfigActorSelection.model_rebuild()
