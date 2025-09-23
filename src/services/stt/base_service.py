from abc import ABC, abstractmethod
from typing import AsyncGenerator, AsyncIterator, Callable, Any

from ..base_service import BaseService


class BaseSttService(BaseService, ABC):
    @abstractmethod
    def speech_to_text(
            self,
            audio_data: bytes
    ) -> str:
        """Convert speech to text."""

    @abstractmethod
    async def speech_to_text_async(
            self,
            audio_data: bytes
    ) -> str:
        """Convert speech to text asynchronously."""

    @abstractmethod
    async def speech_to_text_stream_out(
            self,
            audio_data: bytes
    ) -> AsyncGenerator[str, None]:
        """Convert speech to text asynchronously, streaming output."""

    @abstractmethod
    async def speech_to_text_stream_inout(
            self,
            audio_iterator: AsyncIterator[bytes],
            stream_text_func: Callable[[AsyncGenerator[str, Any]], Any]
    ):
        """Convert speech to text asynchronously, streaming input and output."""
