from enum import Enum
from typing import Union, TYPE_CHECKING

from src.framework import Message, MessageChunk, MessageAudioChunk, MessageAudio
from src.models.messages import EventMessage

# if TYPE_CHECKING:
#     from src.models.messages import IncomingUserMessage, EventMessage


class MessageWsEvents(str, Enum):
    START = 'start'
    END = 'end'
    CHUNK = 'chunk'
    AUDIO = 'audio'
    FULL_MESSAGE = 'full_message'
    USER_MESSAGE = 'user_message'


MessageWsDataTypes = Union[EventMessage, Message, MessageChunk, MessageAudio, MessageAudioChunk]
