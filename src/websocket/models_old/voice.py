from enum import Enum

from src.models.voice import VoiceChunk


class VoiceWsEvents(str, Enum):
    VOICE_CHUNK = "voice_chunk"
    VOICE_END = "voice_end"
    VOICE_ERROR = "voice_error"


VoiceWsDataTypes = VoiceChunk
