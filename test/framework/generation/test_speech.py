import pathlib

import pytest

from src.framework.generation import SpeechToTextGenerator


@pytest.fixture
def audio_path() -> str:
    return str(pathlib.Path(__file__).parent / "harvard.wav")


@pytest.mark.asyncio
class TestSpeechGenerator:

    async def test_run_async(self, audio_path):
        generator = SpeechToTextGenerator()

        transcription = await generator.generate_data_async(audio_path)

        print(transcription)

        assert transcription is not None
        assert transcription != ''
