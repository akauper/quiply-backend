import pathlib
import time

import pytest
from devtools import debug

from src.framework.runnables.generators.models import SpeechToTextGenerationParams, SpeechToTextResponse
from src.framework.runnables.generators.speech_to_text.services.get import get_speech_to_text_generation_service


@pytest.fixture
def generation_params():
    return SpeechToTextGenerationParams()


@pytest.mark.asyncio
class TestWhisper:

    async def test_run_async(self, generation_params):
        start_time = time.time()

        service = get_speech_to_text_generation_service('whisper')
        assert service is not None

        audio_path = str(pathlib.Path(__file__).parent / "harvard.wav")

        response: SpeechToTextResponse = await service.run_async(audio_path, generation_params)

        debug(response)
        assert response is not None

        print(f'Whisper test_run_async took {time.time() - start_time} seconds')
