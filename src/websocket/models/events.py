import uuid
from enum import Enum
from typing import Any, TypeVar, Generic, Callable, Union, Optional
from pydantic import BaseModel, Field, ConfigDict

from pydantic import BaseModel, Field

from src.models.voice import VoiceChunk, VoiceTranscript
from src.framework import Message, MessageChunk, MessageAudioChunk

EventType = str
EventData = Any

T = TypeVar('T', bound=EventType)
D = TypeVar('D', bound=EventData)


class BaseEvent(BaseModel, Generic[T, D]):
    type: EventType
    data: EventData | None = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid'
    )


class ConnectionEventType(str, Enum):
    READY = 'ready'
    ERROR = 'error'
    DISCONNECT = 'disconnect'
    PING = 'ping'
    PONG = 'pong'


class ConnectionReadyEvent(BaseEvent[ConnectionEventType, str]):
    type: ConnectionEventType = ConnectionEventType.READY
    data: str


class ConnectionErrorEvent(BaseEvent[ConnectionEventType, Exception]):
    type: ConnectionEventType = ConnectionEventType.ERROR
    data: str


class ConnectionDisconnectEvent(BaseEvent[ConnectionEventType, str]):
    type: ConnectionEventType = ConnectionEventType.DISCONNECT
    data: str


class ConnectionPingEvent(BaseEvent[ConnectionEventType, str]):
    type: ConnectionEventType = ConnectionEventType.PING
    data: str


class ConnectionPongEvent(BaseEvent[ConnectionEventType, str]):
    type: ConnectionEventType = ConnectionEventType.PONG
    data: str


ConnectionEvent = Union[
    ConnectionReadyEvent,
    ConnectionErrorEvent,
    ConnectionDisconnectEvent,
    ConnectionPingEvent, ConnectionPongEvent
]


class PacketEventType(str, Enum):
    STREAM_START = 'packet_stream_start'
    STREAM_END = 'packet_stream_end'
    STREAM_CHUNK = 'packet_stream_chunk'
    MESSAGE = 'message_packet'
    HISTORY = 'history_packet'
    AUDIO = 'audio_packet'


class PacketStreamStartEvent(BaseEvent[PacketEventType, Message]):
    type: PacketEventType = PacketEventType.STREAM_START
    data: Message


class PacketStreamEndEvent(BaseEvent[PacketEventType, Message]):
    type: PacketEventType = PacketEventType.STREAM_END
    data: Message


class PacketStreamChunkEvent(BaseEvent[PacketEventType, MessageChunk]):
    type: PacketEventType = PacketEventType.STREAM_CHUNK
    data: MessageChunk


class PacketMessageEvent(BaseEvent[PacketEventType, Message]):
    type: PacketEventType = PacketEventType.MESSAGE
    data: Message


class PacketHistoryEvent(BaseEvent[PacketEventType, Message]):
    type: PacketEventType = PacketEventType.HISTORY
    data: Message


class PacketAudioEvent(BaseEvent[PacketEventType, MessageAudioChunk]):
    type: PacketEventType = PacketEventType.AUDIO
    data: MessageAudioChunk


PacketEvent = Union[
    PacketStreamStartEvent,
    PacketStreamEndEvent,
    PacketStreamChunkEvent,
    PacketMessageEvent,
    PacketHistoryEvent,
    PacketAudioEvent
]


class ScenarioEventType(str, Enum):
    ADVANCE_STAGE = 'advance_stage'
    COMPLETE_SCENARIO = 'complete_scenario'
    TYPING_START = 'typing_start'
    TYPING_END = 'typing_end'


class ScenarioAdvanceStageEvent(BaseEvent[ScenarioEventType, str]):
    type: ScenarioEventType = ScenarioEventType.ADVANCE_STAGE
    data: str


class ScenarioCompleteScenarioEvent(BaseEvent[ScenarioEventType, str]):
    type: ScenarioEventType = ScenarioEventType.COMPLETE_SCENARIO
    data: str


class ScenarioTypingStartEvent(BaseEvent[ScenarioEventType, str]):
    type: ScenarioEventType = ScenarioEventType.TYPING_START
    data: str


class ScenarioTypingEndEvent(BaseEvent[ScenarioEventType, str]):
    type: ScenarioEventType = ScenarioEventType.TYPING_END
    data: str


ScenarioEvent = Union[
    ScenarioAdvanceStageEvent,
    ScenarioCompleteScenarioEvent,
    ScenarioTypingStartEvent,
    ScenarioTypingEndEvent
]


class VoiceEventType(str, Enum):
    VOICE_CHUNK = 'voice_chunk'
    VOICE_END = 'voice_end'
    VOICE_ERROR = 'voice_error'
    VOICE_TRANSCRIPT = 'voice_transcript'


class VoiceChunkEvent(BaseEvent[VoiceEventType, VoiceChunk]):
    type: VoiceEventType = VoiceEventType.VOICE_CHUNK
    data: VoiceChunk


class VoiceEndEvent(BaseEvent[VoiceEventType, VoiceChunk]):
    type: VoiceEventType = VoiceEventType.VOICE_END
    data: VoiceChunk


class VoiceErrorEvent(BaseEvent[VoiceEventType, str]):
    type: VoiceEventType = VoiceEventType.VOICE_ERROR
    data: str


class VoiceTranscriptEvent(BaseEvent[VoiceEventType, VoiceTranscript]):
    type: VoiceEventType = VoiceEventType.VOICE_TRANSCRIPT
    data: VoiceTranscript


VoiceEvent = Union[
    VoiceChunkEvent,
    VoiceEndEvent,
    VoiceErrorEvent,
    VoiceTranscriptEvent
]


WebSocketEvent = Union[
    ConnectionEvent,
    PacketEvent,
    ScenarioEvent,
    VoiceEvent
]

WebSocketEventType = Union[
    ConnectionEventType,
    PacketEventType,
    ScenarioEventType,
    VoiceEventType
]


class WebSocketMessage(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requires_response: bool = Field(default=False)
    type: WebSocketEventType
    data: Optional[EventData] = Field(default=None)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid'
    )


def is_connection_event(event: BaseEvent) -> bool:
    return event.type in ConnectionEventType


def is_packet_event(event: BaseEvent) -> bool:
    return event.type in PacketEventType


def is_scenario_event(event: BaseEvent) -> bool:
    return event.type in ScenarioEventType


def is_voice_event(event: BaseEvent) -> bool:
    return event.type in VoiceEventType


def is_websocket_event(event: BaseEvent) -> bool:
    return (
            is_connection_event(event)
            or is_packet_event(event)
            or is_scenario_event(event)
            or is_voice_event(event)
    )
