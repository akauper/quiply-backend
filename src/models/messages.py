from enum import Enum
from typing import Optional, Any

from pydantic import Field

from src.framework import Message, MessageRole


class EventMessageRole(str, Enum):
    description = 'description'
    announcement = 'announcement'


class EventMessage(Message):
    role: EventMessageRole = Field(default=EventMessageRole.description)

    @classmethod
    def from_description(
            cls,
            content: str,
            *,
            scenario_instance_id: Optional[str] = None,
            **metadata: Any
    ) -> 'EventMessage':
        return cls(
            role=EventMessageRole.description,
            content=content,
            scenario_instance_id=scenario_instance_id,
            metadata=metadata,
        )

    @classmethod
    def from_announcement(
            cls,
            content: str,
            *,
            scenario_instance_id: Optional[str] = None,
            **metadata: Any
    ) -> 'EventMessage':
        return cls(
            role=EventMessageRole.announcement,
            content=content,
            scenario_instance_id=scenario_instance_id,
            metadata=metadata,
        )
