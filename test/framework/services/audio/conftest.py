import asyncio
from typing import AsyncIterator

import pytest


@pytest.fixture
def transcription_text() -> str:
    return "Hello world. This is a Quiply transcription."


@pytest.fixture
async def transcription_iterator(transcription_text) -> AsyncIterator[str]:
    for word in transcription_text.split():
        await asyncio.sleep(0.25)
        yield word
