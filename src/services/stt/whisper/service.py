import os
import tempfile
from typing import AsyncIterator, AsyncGenerator, Any, Callable

import openai

from ..base_service import BaseSttService
from src.utils import logger


class WhisperSttService(BaseSttService):
    def speech_to_text(
            self,
            audio_data: bytes
    ) -> str:
        # Step 1: Save the audio data to a temporary .wav file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file_name = temp_file.name
        temp_file.write(audio_data)
        temp_file.close()

        transcript = ''

        try:
            with open(temp_file_name, 'rb') as audio_file:
                response = openai.Audio.transcribe('whisper-1', audio_file)
                transcript = response.text
                logger.info(f'STT Transcript: {transcript}')
        finally:
            # print(f"Debug Mode: Audio file saved at {temp_file_name}")
            if not self.is_file_locked(temp_file_name):
                os.remove(temp_file_name)
            else:
                logger.error(f"File {temp_file_name} is locked, not removing")

        return transcript

    async def speech_to_text_async(
            self,
            audio_data: bytes
    ) -> str:
        raise NotImplementedError

    async def speech_to_text_stream_out(
            self,
            audio_data: bytes
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def speech_to_text_stream_inout(
            self,
            audio_iterator: AsyncIterator[bytes],
            stream_text_func: Callable[[AsyncGenerator[str, Any]], Any]
    ):
        raise NotImplementedError

    @staticmethod
    def is_file_locked(file_path: str) -> bool:
        locked = None
        file_object = None
        if os.path.exists(file_path):
            try:
                file_object = open(file_path, 'a')
            except IOError as e:
                locked = True
            else:
                locked = False
            finally:
                if file_object:
                    file_object.close()
        return locked
