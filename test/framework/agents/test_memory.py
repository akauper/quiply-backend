import pytest
from src.framework.runnables.agents.memory import ConversationMemory, ConversationSummaryMemory
from src.framework.models import Message, MessageRole


@pytest.fixture
def very_long_message():
    return Message.from_user("This is a very long message. " * 500, 'testing_user')


class TestMemory:
    def test_init_memory(self):
        memory = ConversationMemory()
        assert memory.buffer == []

    def test_init_summary_memory(self):
        memory = ConversationSummaryMemory()
        assert memory.buffer == []
        assert memory.summary_generator is not None
        assert memory.max_buffer_tokens == 2100
        assert memory.summarize_prompt is not None
        assert memory.moving_summary_buffer == ""

    def test_memory_save_and_load(self, chat_messages):
        memory = ConversationMemory()

        for i in range(2):
            memory.save(chat_messages)
            assert len(memory.buffer) == len(chat_messages)

            buffer = memory.load()
            assert len(buffer) == len(chat_messages)
            if i == 0:
                memory.clear()

    def test_summary_memory_save_and_load(self, chat_messages):
        memory = ConversationSummaryMemory()

        for i in range(2):
            memory.save(chat_messages)
            assert len(memory.buffer) == len(chat_messages)

            buffer = memory.load()
            assert len(buffer) == len(chat_messages)
            if i == 0:
                memory.clear()

    def test_summary_memory_prune(self, chat_messages, very_long_message):
        memory = ConversationSummaryMemory()

        memory.save(chat_messages)
        memory.save(very_long_message)
        assert len(memory.buffer) == 2
        assert memory.get_token_count() < memory.max_buffer_tokens
        assert Message.is_from(memory.buffer[1], MessageRole.summary)
        assert memory.moving_summary_buffer != ""
        print(memory.to_string())

