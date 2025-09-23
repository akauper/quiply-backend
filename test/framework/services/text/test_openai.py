import time

import pytest

from src.framework.runnables.generators.models import TextResponse, TextGenerationParams
from src.framework.models import Message
from src.framework.runnables.generators.text.services.get import get_text_generation_service
from test.framework.test_utils import assert_valid_text_response, assert_valid_text_response_chunk


@pytest.fixture
def chat_messages():
    return [
        Message.from_system("You are a helpful assistant"),
        Message.from_user("What's the capital of France"),
    ]


@pytest.fixture
def generation_params():
    return TextGenerationParams()


@pytest.mark.asyncio
class TestOpenAiGenerationService:

    async def test_run_async(self, chat_messages, mock_chat_completion, generation_params):
        start_time = time.time()
        service = get_text_generation_service('openai')
        assert service is not None

        text_response: TextResponse = await service.run_async(chat_messages, generation_params)
        print(text_response)
        assert_valid_text_response(text_response)
        print(f'OpenAI test_run_async took {time.time() - start_time} seconds')

    async def test_run_async_with_params(self, chat_messages, mock_chat_completion):
        start_time = time.time()
        service = get_text_generation_service('openai')
        assert service is not None

        generation_params = TextGenerationParams(max_tokens=10, temperature=0.5)
        text_response: TextResponse = await service.run_async(chat_messages, generation_params=generation_params)
        # check that the component calls the OpenAI API with the correct parameters
        _, kwargs = mock_chat_completion.call_args
        assert kwargs["max_tokens"] == 10
        assert kwargs["temperature"] == 0.5

        print(text_response)
        assert_valid_text_response(text_response)
        print(f'OpenAI test_run_async_with_params took {time.time() - start_time} seconds')

    async def test_run_stream(self, chat_messages, generation_params):
        start_time = time.time()
        service = get_text_generation_service('openai')
        assert service is not None

        async_generator = await service.run_stream(chat_messages, generation_params)

        chunks = []
        async for chunk in async_generator:
            print(chunk.content)
            assert_valid_text_response_chunk(chunk)
            chunks.append(chunk)

        text_response = TextResponse.from_chunks(chunks)
        assert_valid_text_response(text_response)
        print(f'OpenAI test_run_stream took {time.time() - start_time} seconds')
