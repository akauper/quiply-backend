import asyncio
from typing import Optional, AsyncIterator, Callable, List

from pydantic import Field, BaseModel

from .base import UIDObject


class VoiceTranscript(BaseModel):
    """
    Represents a transcript of an audio input chunk.
    """

    stream_id: str
    """ The id of the stream this transcript belongs to."""

    chunk_id: str
    """ The id of the chunk this transcript belongs to."""

    text: str
    """ The transcript of the audio input chunk."""

    is_final: bool = Field(default=False)
    """ Whether this transcript is the final transcript in a streaming request."""


class VoiceStreamSettings(BaseModel):
    """
    Represents the settings for a voice stream.
    """

    format: str
    """ The format of the stream. """

    chunk_timeslice: int
    """ The timeslice in milliseconds for each chunk in the stream. """

    device_id: Optional[str] = Field(default=None)
    """ The id of the device to use for the stream. """

    group_id: Optional[str] = Field(default=None)
    """ The id of the group to use for the stream. """

    sample_rate: Optional[int] = Field(default=None)
    """ The sample rate to use for the stream. """

    sample_size: Optional[int] = Field(default=None)
    """ The sample size to use for the stream. """


class VoiceChunk(UIDObject):
    """
    Represents an audio input chunk from the frontend.
    """

    created_at: str
    """ The time at which this chunk was created in iso format."""

    stream_id: str
    """ The id of the stream this chunk belongs to."""

    index: int
    """The index of this audio input chunk in the sequence of chunks."""

    audio: Optional[str] = Field(default=None)
    """The audio data in base64 format."""

    is_final: bool = Field(default=False)
    """Whether this chunk is the final chunk in a streaming request."""

    settings: Optional[VoiceStreamSettings] = Field(default=None)
    """ The settings for the stream. Only used for the first chunk. """

    @property
    def is_start(self) -> bool:
        return self.index == 0

    def create_transcript(self, text: str) -> VoiceTranscript:
        return VoiceTranscript(
            stream_id=self.stream_id,
            chunk_id=self.uid,
            text=text,
            is_final=self.is_final or False
        )


class VoiceStream(AsyncIterator[VoiceChunk]):
    id: str
    """ The id of the stream."""

    settings: VoiceStreamSettings
    """ The settings for the stream."""

    queue: asyncio.Queue[VoiceChunk]
    """ The queue of audio chunks."""

    stream_ended: bool = False
    """ Whether the stream has ended."""

    _on_end_callbacks: List[Callable[[str], None]] = []

    def __init__(self, stream_id: str, settings: VoiceStreamSettings):
        self.id = stream_id
        self.settings = settings
        self.queue = asyncio.Queue()

    def add_chunk(self, chunk: VoiceChunk):
        self.queue.put_nowait(chunk)
        if chunk.is_final:
            self._end_stream()

    async def __anext__(self) -> VoiceChunk:
        if self.stream_ended and self.queue.empty():
            raise StopAsyncIteration
        return await self.queue.get()

    def _end_stream(self):
        self.stream_ended = True
        for callback in self._on_end_callbacks:
            callback(self.id)
        self._on_end_callbacks.clear()

    def on_end(self, callback: Callable[[str], None]):
        self._on_end_callbacks.append(callback)

    def off_end(self, callback: Callable[[str], None]):
        self._on_end_callbacks.remove(callback)
