import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator, AsyncIterator

import torch
import whisper

from src.framework.exceptions import GenerationException
from src.framework.utils import CreateWavFile
from .converter import WhisperGenerationConverter
from ..base import BaseSpeechToTextGenerationService
from ...models import SpeechToTextGenerationParams, SpeechToTextResponse, SpeechToTextRequest


class WhisperGenerationService(BaseSpeechToTextGenerationService):
    converter: WhisperGenerationConverter

    def __init__(self):
        super().__init__()
        self.converter = WhisperGenerationConverter()

    def _transcribe(
            self,
            request: SpeechToTextRequest,
            generation_params: SpeechToTextGenerationParams,
    ) -> SpeechToTextResponse:
        if request is None:
            raise ValueError('SpeechToTextGenerationRequest cannot be None')

        try:
            with CreateWavFile(request, mime_type='audio/webm;codec=opus') as file_path:
                audio = whisper.load_audio(file_path)

            device = torch.device("cuda" if torch.cuda.is_available() and generation_params.device == 'cuda' else "cpu")
            model = whisper.load_model(generation_params.model, device)
            options = self.converter.to_decoding_options(generation_params)

            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            decoding_result = whisper.decode(model, mel, options)

            result = self.converter.from_decoding_result(decoding_result)
        except Exception as e:
            raise GenerationException(
                message=f'Error while generating speech to text: {e}',
                inner_exception=e
            )

        return result

    async def run_async(
            self,
            request: SpeechToTextRequest,
            generation_params: SpeechToTextGenerationParams,
    ) -> SpeechToTextResponse:
        try:
            loop = asyncio.get_event_loop()

            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, self._transcribe, request, generation_params)
        except Exception as e:
            raise GenerationException(
                message=f'Error while generating speech to text async: {e}',
                inner_exception=e
            )

        return result

    async def run_stream(
            self,
            request: AsyncIterator[SpeechToTextRequest],
            generation_params: SpeechToTextGenerationParams,
    ) -> AsyncGenerator[SpeechToTextResponse, None]:
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)

        try:
            async for chunk in request:
                await queue.put(chunk)

                if queue.full():
                    data = b''
                    while not queue.empty():
                        data += await queue.get()
                    response = await self.run_async(data, generation_params)
                    yield response
        except Exception as e:
            raise GenerationException(
                message=f'Error while generating speech to text stream: {e}',
                inner_exception=e
            )


