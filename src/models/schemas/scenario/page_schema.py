from enum import Enum
from typing import Any, Optional, Union, List

from pydantic import BaseModel, Field

from .page_field_schema import FieldSchemaType, FieldCondition, FieldSchema


class PageSchemaType(str, Enum):
    FIELDS = 'fields'
    ACTOR_SELECTION = 'actor_selection'
    REVIEW = 'review'


class PageSchemaOperator(str, Enum):
    EQUALS = 'equals'
    NOT_EQUALS = 'not_equals'


class PageSchemaCondition(BaseModel):
    page_value: str
    operator: PageSchemaOperator
    value: Any


class PageSchemaBase(BaseModel):
    type: PageSchemaType = PageSchemaType.FIELDS
    uid: str

    instruction: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

    visible_if: Optional[PageSchemaCondition] = None
    """ A condition that must be met for the page to be visible. """


class PageSchemaFields(PageSchemaBase):
    type: PageSchemaType = PageSchemaType.FIELDS

    fields: List[FieldSchema] = Field(default_factory=list)


class PageSchemaActorSelection(PageSchemaBase):
    type: PageSchemaType = PageSchemaType.ACTOR_SELECTION
    uid: str = 'actor_selection'
    title: str = 'Actors'
    instruction: str = 'Select the actors for this scenario.'


class PageSchemaReview(PageSchemaBase):
    type: PageSchemaType = PageSchemaType.REVIEW
    uid: str = 'review'


PageSchema = Union[
    PageSchemaFields,
    PageSchemaActorSelection,
    PageSchemaReview
]

PageSchemaFields.model_rebuild()
PageSchemaActorSelection.model_rebuild()
PageSchemaReview.model_rebuild()
