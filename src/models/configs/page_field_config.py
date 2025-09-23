from typing import List, Union

from pydantic import BaseModel, Field
from ..schemas.scenario.page_field_schema import FieldSchema, FieldSchemaType, ScenarioFieldTemplateImageSelectOption
from ..schemas.scenario.page_schema import PageSchema


class ScenarioFieldConfigBase(BaseModel):
    field_schema_type: FieldSchemaType
    field_schema_uid: str

    def get_field_template(self, page_schema: PageSchema) -> FieldSchema:
        for field_schema in page_schema.fields:
            if field_schema.uid == self.field_schema_uid:
                return field_schema
        raise ValueError(f'Field template not found: {self.field_schema_uid}')


class ScenarioFieldConfigText(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.TEXT
    field_schema_uid: str = 'text'
    value: str


class ScenarioFieldConfigToggle(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.TOGGLE
    field_schema_uid: str = 'toggle'
    value: bool


class ScenarioFieldConfigNumber(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.NUMBER
    field_schema_uid: str = 'number'
    value: int


class ScenarioFieldConfigSelect(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.SELECT
    field_schema_uid: str = 'select'
    value: str


class ScenarioFieldConfigMultiSelect(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.MULTI_SELECT
    field_schema_uid: str = 'multi_select'
    values: List[str] = Field(default_factory=list[str])


class ScenarioFieldConfigImageSelect(ScenarioFieldConfigBase):
    field_schema_type: FieldSchemaType = FieldSchemaType.IMAGE_SELECT
    field_schema_uid: str = 'image_select'
    value: ScenarioFieldTemplateImageSelectOption


ScenarioFieldConfig = Union[
    ScenarioFieldConfigText,
    ScenarioFieldConfigToggle,
    ScenarioFieldConfigNumber,
    ScenarioFieldConfigSelect,
    ScenarioFieldConfigMultiSelect,
    ScenarioFieldConfigImageSelect
]


ScenarioFieldConfigText.model_rebuild()
ScenarioFieldConfigToggle.model_rebuild()
ScenarioFieldConfigNumber.model_rebuild()
ScenarioFieldConfigSelect.model_rebuild()
ScenarioFieldConfigMultiSelect.model_rebuild()
ScenarioFieldConfigImageSelect.model_rebuild()
