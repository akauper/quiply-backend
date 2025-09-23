from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, AsyncGenerator

from ..models import DiarizationGenerationParams, DiarizationResponse, DiarizationRequest


class BaseSpeechDiarizationService(ABC):

    @abstractmethod
    def run(
            self,
            request: DiarizationRequest,
            generation_params: DiarizationGenerationParams
    ) -> DiarizationResponse:
        pass

    @abstractmethod
    async def run_async(
            self,
            request: DiarizationRequest,
            generation_params: DiarizationGenerationParams
    ) -> DiarizationResponse:
        pass

    @abstractmethod
    def run_stream(
            self,
            request: AsyncIterator[DiarizationRequest],
            generation_params: DiarizationGenerationParams,
            **stream_settings_kwargs: Any
    ) -> AsyncGenerator[DiarizationResponse, None]:
        """
        :param request: AsyncIterator[DiarizationRequest]
        :param generation_params: DiarizationGenerationParams
        :param stream_settings_kwargs: Any
        :return: AsyncGenerator[DiarizationResponse]
        """
        pass
