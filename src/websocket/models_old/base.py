import uuid
from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel, Field

from .connection import ConnectionWsEvents
from .debug import DebugWsEvents
from .message import MessageWsEvents, MessageWsDataTypes
from .scenario import ScenarioWsEvents, ScenarioWsDataTypes
from .voice import VoiceWsEvents, VoiceWsDataTypes


class BaseWsEvents(str, Enum):
    TYPING_START = 'typing_start'
    TYPING_STOP = 'typing_stop'


WebSocketEvents = Union[
    BaseWsEvents,
    ScenarioWsEvents,
    MessageWsEvents,
    ConnectionWsEvents,
    DebugWsEvents,
    VoiceWsEvents
]


WebSocketDataTypes = Union[
    VoiceWsDataTypes,
    ScenarioWsDataTypes,
    MessageWsDataTypes,
    str,
    None,
]


class WebSocketMessage(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event: WebSocketEvents
    requires_response: bool = Field(default=False)
    data: Optional[WebSocketDataTypes] = Field(default=None)
