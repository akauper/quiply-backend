from devtools import debug

from src.framework.runnables.agents.agent import Agent
from src.framework.models import Message


class TestAgent:
    def test_agent_pretty(self):
        from src.framework.prompting import prompts
        prompt = prompts.character.common_instructions

        agent = Agent()
        agent.add_message(Message.from_system(prompt.template))

        debug(agent)
    # def test_agent_add_message(self, chat_messages):
    #     agent = Agent()
    #     agent.add_message(chat_messages)
    #     assert len(agent.memory.buffer) == 2
    #
    # @pytest.mark.asyncio
    # async def test_agent_run_async(self, chat_messages):
    #     agent = Agent()
    #     agent.add_message(chat_messages)
    #
    #     response_message: Message = await agent.run_async()
    #
    #     print(response_message)
    #     assert response_message.is_from(MessageRole.ai)
    #     assert response_message.content != ""
    #
    # @pytest.mark.asyncio
    # async def test_agent_memory(self, memory_messages):
    #     agent = Agent()
    #     agent.add_message(memory_messages)
    #
    #     response_message: Message = await agent.run_async(Message.from_user("What is my name?"))
    #
    #     print(response_message)
    #     assert response_message.is_from(MessageRole.ai)
    #     assert response_message.content != ""
    #     assert 'jacob carpenter' in response_message.content.lower()
    #
    # @pytest.mark.asyncio
    # async def test_agent_run_stream(self, chat_messages):
    #     agent = Agent()
    #     agent.add_message(chat_messages)
    #
    #     def process_chunk(chunk: MessageChunk):
    #         print(chunk)
    #         assert chunk.role == MessageRole.ai
    #         assert chunk.content != ""
    #
    #     response_message: Message = await agent.run_async_stream(message_chunk_callback=process_chunk)
    #
    #     print(response_message)
    #     assert response_message.is_from(MessageRole.ai)
    #     assert response_message.content != ""
    #
    # @pytest.mark.asyncio
    # async def test_agent_run_stream_with_audio(self, chat_messages):
    #     agent_text_generator = TextGenerator(generation_params=TextGenerationParams(max_tokens=35))
    #     agent = Agent(text_generator=agent_text_generator)
    #     agent.add_message(chat_messages)
    #
    #     got_final_audio_chunk = False
    #
    #     def process_chunk(chunk: MessageChunk):
    #         print(f'Text Chunk: {chunk}')
    #         assert chunk.role == MessageRole.ai
    #
    #     def process_audio_chunk(chunk: MessageAudioChunk):
    #         if chunk.index == 0:
    #             print("Start of audio")
    #         elif chunk.is_final:
    #             nonlocal got_final_audio_chunk
    #             got_final_audio_chunk = True
    #             print("End of audio")
    #         else:
    #             print(f'Got Chunk. Has Audio: {chunk.audio and len(chunk.audio) > 0}. Message ID: {chunk.message_id}')
    #
    #         assert chunk is not None
    #         assert chunk.message_audio_id is not None
    #         assert chunk.message_id is not None
    #
    #     response_message: Message = await agent.run_async_stream(message_chunk_callback=process_chunk, audio_chunk_callback=process_audio_chunk)
    #
    #     print(response_message)
    #     assert response_message.is_from(MessageRole.ai)
    #     assert response_message.content is not None
    #     assert response_message.content != ""
    #
    #     while not got_final_audio_chunk:
    #         await asyncio.sleep(0.1)
