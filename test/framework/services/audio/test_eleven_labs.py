import pytest

from src.framework.runnables.generators.audio.services.get import get_audio_generation_service
from src.framework.runnables.generators.models import AudioResponse, AudioGenerationParams
from test.framework.test_utils import assert_valid_audio_response_chunks, \
    assert_valid_audio_response


@pytest.fixture
def generation_params():
    return AudioGenerationParams()


@pytest.mark.asyncio
class TestElevenLabsGenerationService:

    async def test_generate_async(self, generation_params):
        service = get_audio_generation_service('eleven_labs')
        assert service is not None

        audio_response: AudioResponse = await service.generate_async("Hello world", generation_params)
        assert audio_response is not None

    async def test_generate_async_stream_output(self, transcription_text, generation_params):
        service = get_audio_generation_service('eleven_labs')
        assert service is not None

        async_generator = service.generate_stream_output(transcription_text, generation_params)

        chunks = []
        async for chunk in async_generator:
            if chunk.is_start:
                print("Start of audio")
            elif chunk.is_final:
                print("End of audio")
            else:
                print(f'Has Audio: {chunk.audio and len(chunk.audio) > 0}')
            chunks.append(chunk)

        assert_valid_audio_response_chunks(chunks)

        audio_response = AudioResponse.from_chunks(chunks)
        assert_valid_audio_response(audio_response)

    async def test_generate_async_stream_full_duplex(self, transcription_iterator, generation_params):
        service = get_audio_generation_service('eleven_labs')
        assert service is not None

        async_generator = service.generate_stream_full_duplex(transcription_iterator, generation_params)

        chunks = []
        async for chunk in async_generator:
            if chunk.is_start:
                print("Start of audio")
            elif chunk.is_final:
                print("End of audio")
            else:
                print(f'Has Audio: {chunk.audio and len(chunk.audio) > 0}')
            chunks.append(chunk)

        assert_valid_audio_response_chunks(chunks)

        audio_response = AudioResponse.from_chunks(chunks)
        # print(audio_response)
        assert_valid_audio_response(audio_response)
