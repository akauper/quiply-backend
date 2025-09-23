import asyncio
from typing import AsyncIterator

import pytest
from devtools import debug

from src.framework.runnables.generators.audio.models import AudioResponse
from src.framework.runnables.generators.audio import AudioGenerator
from test.framework.test_utils import assert_valid_audio_response

@pytest.fixture
def transcription_text() -> str:
    return "Hello world. This is a Quiply transcription."


@pytest.fixture
async def transcription_iterator(transcription_text) -> AsyncIterator[str]:
    for word in transcription_text.split():
        await asyncio.sleep(0.25)
        yield word


@pytest.mark.asyncio
class TestAudioGenerator:

    # async def test_run_async(self, transcription_text):
    #     generator = AudioGenerator()
    #
    #     audio_response: AudioResponse = await generator.run_async(transcription_text)
    #     assert_valid_audio_response(audio_response)
    #     debug(audio_response)

    # async def test_run_async_stream_output(self, transcription_text):
    #     generator = AudioGenerator()
    #
    #     async_generator = generator.run_stream(transcription_text)
    #
    #     chunks = []
    #     async for chunk in async_generator:
    #         if chunk.is_start:
    #             print("Start of audio")
    #         elif chunk.is_final:
    #             print("End of audio")
    #         else:
    #             print(f'Has Audio: {chunk.audio and len(chunk.audio) > 0}')
    #         chunks.append(chunk)
    #
    #     audio_response = AudioResponse.from_chunks(chunks)
    #     assert_valid_audio_response(audio_response)
    #
    async def test_run_async_stream_full_duplex(self, transcription_iterator):
        generator = AudioGenerator()

        async_generator = generator.run_stream(transcription_iterator)

        chunks = []
        async for chunk in async_generator:
            if chunk.is_start:
                print("Start of audio")
            elif chunk.is_final:
                print("End of audio")
            else:
                print(f'Has Audio: {chunk.audio and len(chunk.audio) > 0}')
                print(chunk.normalized_alignment)
            chunks.append(chunk)

        audio_response = AudioResponse.from_chunks(chunks)
        assert_valid_audio_response(audio_response)
