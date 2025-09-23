from typing import TypeVar, AsyncGenerator, AsyncIterator, ClassVar

from pydantic import Field

from src.framework.exceptions import GenerationException
from .models import DiarizationGenerationParams, DiarizationRequest, DiarizationResponse
from .services import BaseSpeechDiarizationService, get_speech_diarization_service
from ..base import BaseGenerator

TGenerationService = TypeVar("TGenerationService", bound=BaseSpeechDiarizationService)


class DiarizationGenerator(BaseGenerator[DiarizationGenerationParams]):
    # service_name: str = Field(default=_DEFAULT_SERVICE_NAME)
    # generation_params: DiarizationGenerationParams = Field(default_factory=DiarizationGenerationParams)

    generator_name: ClassVar[str] = 'diarization'

    def cleanup(self):
        del self.generation_params
        super().cleanup()

    def _get_generation_service(self) -> TGenerationService:
        try:
            return get_speech_diarization_service(self.service_name)
        except NotImplementedError as e:
            raise GenerationException(
                message=f'Generation service {self.service_name} is not implemented',
                inner_exception=e
            )

    def run(
            self,
            request: DiarizationRequest,
    ) -> DiarizationResponse:
        context = self._begin_run(generation_params=self.generation_params)
        generation_service = self._get_generation_service()

        self._invoke_callback('on_diarization_generation_start', request=request, **context)

        try:
            response = generation_service.run(
                request=request,
                generation_params=self.generation_params
            )
        except Exception as e:
            self._invoke_callback('on_diarization_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating diarization: {e}',
                inner_exception=e
            )

        self._invoke_callback('on_diarization_generation_end', response=response, **context)

        return response

    async def run_async(
            self,
            request: DiarizationRequest,
    ) -> DiarizationResponse:
        context = self._begin_run(generation_params=self.generation_params)
        generation_service = self._get_generation_service()

        await self._invoke_callback_async('on_diarization_generation_start', request=request, **context)

        try:
            response = await generation_service.run_async(
                request=request,
                generation_params=self.generation_params
            )
        except Exception as e:
            await self._invoke_callback_async('on_diarization_generation_error', error=e, **context)
            raise GenerationException(
                message=f'Error while generating diarization: {e}',
                inner_exception=e
            )

        await self._invoke_callback_async('on_diarization_generation_end', response=response, **context)

        return response

    async def run_stream(
            self,
            request: AsyncIterator[DiarizationRequest],
    ) -> AsyncGenerator[DiarizationResponse, None]:
        raise NotImplementedError()

        # context = self._get_context(generation_params=self.generation_params)
        # generation_service = self._get_generation_service()
        #
        # await self._invoke_callback_async('on_diarization_generation_start', request=request, **context)
        #
        # try:
        #     generator = generation_service.run_stream(
        #         request=request,
        #         generation_params=self.generation_params
        #     )
        # except Exception as e:
        #     await self._invoke_callback_async('on_diarization_generation_error', error=e, **context)
        #     raise GenerationException(
        #         message=f'Error while generating diarization: {e}',
        #         inner_exception=e
        #     )
        #
        # chunks: List[DiarizationResponse] = []
        #
        # async for chunk in generator:
        #     chunks.append(chunk)
        #     await self._invoke_callback_async('on_diarization_generation_chunk', chunk=chunk, **context)
        #     yield chunk
        #
        #
        #
        # await self._invoke_callback_async('on_diarization_generation_end', response=response, **context)
        #
        # return response