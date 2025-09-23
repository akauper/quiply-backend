from enum import Enum
from typing import Optional, List, Union, Any

from pydantic import BaseModel, Field

from ...data.media import LocalImageMixin


class FieldSchemaType(str, Enum):
    UNSET = "unset"
    TEXT = "text"
    TOGGLE = "toggle"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    IMAGE_SELECT = "image_select"


class FieldCondition(BaseModel):
    field: str
    operator: str
    value: Any


class FieldSchemaBase(BaseModel):
    type: FieldSchemaType = FieldSchemaType.UNSET

    uid: str

    label: Optional[str] = None
    """ The label to display. """

    required: bool = False
    """ Whether a value is required for this field in order to start the scenario. """

    primary_field: Optional[bool] = False
    """ Whether this field is the primary field for the scenario. Primary fields are displayed on the result card. """

    help_text: Optional[str] = None
    """ Additional text to display to help the user understand the field. """

    error_message: Optional[str] = None
    """ The error message to display if the user does not provide a value for the field. """

    visible_if: Optional[FieldCondition] = None
    """ A condition that must be met for the field to be visible. """


class FieldSchemaText(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.TEXT

    placeholder: Optional[str] = None
    """ The placeholder text to display when the field is empty. """

    random_options: Optional[List[str]] = Field(default_factory=list)
    """ A list of options to randomly select from for the value. """


class FieldSchemaToggle(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.TOGGLE

    on_label: str = "On"
    """ The label to display when the toggle is on. """

    off_label: str = "Off"
    """ The label to display when the toggle is off. """


class FieldSchemaNumber(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.NUMBER

    min: Optional[float] = None
    """ The minimum value allowed. """

    max: Optional[float] = None
    """ The maximum value allowed. """

    step: Optional[float] = None
    """ The step value for the input. """


class FieldSchemaSelect(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.SELECT

    options: List[str]
    """ The list of options to select from. """

    default_option: Optional[str] = None
    """ The default option to select. """


class FieldSchemaMultiSelect(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.MULTI_SELECT

    options: List[str]
    """ The list of options to select from. """

    default_options: Optional[List[str]] = None
    """ The default options to select. """


class ScenarioFieldTemplateImageSelectOption(BaseModel, LocalImageMixin):
    uid: str
    title: str = ""
    subtitle: Optional[str] = None
    description: Optional[str] = None


class FieldSchemaImageSelect(FieldSchemaBase):
    type: FieldSchemaType = FieldSchemaType.IMAGE_SELECT

    options: List[ScenarioFieldTemplateImageSelectOption]
    """ The list of options to select from. """

    default_option: Optional[str] = None
    """ The default option to select. """


FieldSchema = Union[
    FieldSchemaText,
    FieldSchemaToggle,
    FieldSchemaNumber,
    FieldSchemaSelect,
    FieldSchemaMultiSelect,
    FieldSchemaImageSelect,
]

FieldSchemaText.model_rebuild()
FieldSchemaToggle.model_rebuild()
FieldSchemaNumber.model_rebuild()
FieldSchemaSelect.model_rebuild()
FieldSchemaMultiSelect.model_rebuild()
FieldSchemaImageSelect.model_rebuild()
FieldSchemaBase.model_rebuild()
