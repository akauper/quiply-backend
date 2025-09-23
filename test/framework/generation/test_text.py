import pytest
from devtools import debug

from src.framework import Message
from src.framework.runnables.generators import TextGenerator
from src.framework.runnables.generators.text.models import TextResponse, TextResponseChunk, TextGenerationParams
from test.framework.test_utils import assert_valid_text_response, assert_valid_text_response_chunk


@pytest.fixture
def chat_messages():
    return [
        # Message.from_system("You are a helpful assistant"),
        Message.from_user("What's the capital of France"),
    ]


@pytest.mark.asyncio
class TestTextGenerator:

    # async def test_run_async(self, chat_messages):
    #     generation_params: TextGenerationParams = TextGenerationParams(model='claude-3-5-sonnet-20240620')
    #     generator = TextGenerator(generation_params=generation_params)
    #
    #     text_response: TextResponse = await generator.run_async(chat_messages)
    #     assert_valid_text_response(text_response)
    #     print(text_response)

    async def test_run_stream(self, chat_messages):
        generator = TextGenerator()

        async_generator = generator.run_stream(chat_messages)

        chunks = []
        async for chunk in async_generator:
            debug(chunk)
            chunks.append(chunk)

        text_response = TextResponse.from_chunks(chunks)
        debug(text_response)
        assert_valid_text_response(text_response)

# @pytest.mark.asyncio
# async def test_run_async():
#     generator = Generator
#     with patch('your_module.generator.get_generation_service', return_value=mock_generation_service):
#         generator = Generator()
#         request: List[QMessage] = [
#             QMessage(
#                 author_id='test',
#                 author_name='test',
#                 has_audio=False,
#                 content='Tell me a short story',
#                 scenario_instance_id='test',
#                 type=QMessageType.user,
#             )
#         ]
#         completion = await generator.run_async(request)
#
#         # Assertions to validate behavior
#         assert completion is not None  # replace with more specific assertions as needed
#         mock_generation_service.complete_async.assert_called_once_with(
#             request=request,
#             generation_params=generator.generation_params,
#             runnable_params=generator.runnable_params,
#         )

# Additional tests can be added similarly
