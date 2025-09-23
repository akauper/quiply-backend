from typing import Optional, List, Dict, Literal

from pydantic import Field, ConfigDict

from ..base import SerializableObject


SUPPORTED_CONTENT_TYPES = [
    'application/pdf',
    'text/plain',
    'text/csv',
    'text/html',
    # 'application/json',
    'text/markdown'
]


class ContextReference(SerializableObject):
    """ContextReference can contain either a url reference to a ContextValue object, or a string value directly"""
    user_id: str
    context_template_uid: str
    name: str

    scenario_schema_id: Optional[str] = Field(default=None)
    reference_type: Literal['string', 'file']

    value: str
