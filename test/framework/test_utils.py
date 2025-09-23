from typing import List

from src.framework.runnables.generators import TextResponse, TextChoice, TextResponseChunk, TextChoiceChunk, AudioResponse, \
    AudioResponseChunk


def assert_valid_text_response(text_response: TextResponse):
    assert text_response is not None
    assert text_response.choices is not None
    assert len(text_response.choices) > 0
    assert text_response.choices[0] is not None
    assert_valid_text_choice(text_response.choices[0])
    assert text_response.model is not None


def assert_valid_text_choice(text_choice: TextChoice):
    assert text_choice is not None
    assert text_choice.content is not None


def assert_valid_text_response_chunk(chunk: TextResponseChunk):
    assert chunk is not None


def assert_valid_text_choice_chunk(chunk: TextChoiceChunk):
    assert chunk is not None
    if chunk.finish_reason is None:
        assert chunk.content is not None


def assert_valid_audio_response(audio_response: AudioResponse):
    assert audio_response is not None
    assert audio_response.audio is not None
    assert len(audio_response.audio) > 0


def assert_valid_audio_response_chunks(chunks: List[AudioResponseChunk]):
    assert chunks is not None
    assert len(chunks) > 0
    assert chunks[0].is_start
    assert chunks[-1].is_final