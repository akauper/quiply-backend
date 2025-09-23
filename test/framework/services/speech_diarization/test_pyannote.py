import pathlib
import time

import pytest
from devtools import debug

from src.framework.services.speech_diarization import get_speech_diarization_service
from src.framework.runnables.generators.models import DiarizationGenerationParams, DiarizationResponse


@pytest.fixture
def audio_file_path():
    return str(pathlib.Path(__file__).parent / "harvard.wav")
    # return str(pathlib.Path(__file__).parent / "webmaudio.webm")


@pytest.mark.asyncio
class TestPyannoteSpeechDiarizationService:
    # @pytest.mark.parametrize(
    #     "request, expected",
    #     [
    #         pytest.param(
    #             "request0",
    #             "expected0",
    #             id="id0",
    #         ),
    #         pytest.param(
    #             "request1",
    #             "expected1",
    #             id="id1",
    #         ),
    #     ],
    # )

    async def test_run_async(self, request, audio_file_path):
        start_time = time.time()

        service = get_speech_diarization_service('pyannote')
        assert service is not None

        response: DiarizationResponse = await service.generate_data_async(audio_file_path, DiarizationGenerationParams())

        debug(response)

        assert response is not None

        print(f'Pyannote test_run_async took {time.time() - start_time} seconds')