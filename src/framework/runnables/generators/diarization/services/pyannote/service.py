import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncIterator, AsyncGenerator, Any, Dict, Optional

import torch
from dotenv import load_dotenv
from pyannote.audio import Model, Pipeline
from pyannote.audio.pipelines import VoiceActivityDetection
from pyannote.core.annotation import Annotation

from framework import framework_settings
from src.framework.utils import CreateWavFile
from src.utils import loggers
from .converter import PyannoteSpeechDiarizationConverter
from ..base import BaseSpeechDiarizationService
from ...models import DiarizationGenerationParams, DiarizationResponse, DiarizationRequest


class PyannoteSpeechDiarizationService(BaseSpeechDiarizationService):
    converter: PyannoteSpeechDiarizationConverter

    detection_model: Model = Model.from_pretrained(
        framework_settings.runnables.generators.diarization.services.pyannote.detection_checkpoint or "pyannote/segmentation-3.0",
        use_auth_token=os.environ.get('HF_TOKEN')
    )

    diarization_pipeline: Pipeline = Pipeline.from_pretrained(
        framework_settings.runnables.generators.diarization.services.pyannote.diarization_checkpoint or "pyannote/speaker-diarization-3.1",
        use_auth_token=os.environ.get('HF_TOKEN')
    )

    def __init__(self):
        super().__init__()

        self.converter = PyannoteSpeechDiarizationConverter()

    def run(
            self,
            request: DiarizationRequest,
            generation_params: DiarizationGenerationParams
    ) -> DiarizationResponse:
        if request is None:
            raise ValueError("DiarizationRequest cannot be None")

        response = self._sync(request, generation_params)

        loggers.framework.dev_debug(response)

        return response

    async def run_async(
            self,
            request: DiarizationRequest,
            generation_params: DiarizationGenerationParams
    ) -> DiarizationResponse:
        if request is None:
            raise ValueError("DiarizationRequest cannot be None")

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            response = await loop.run_in_executor(executor, self._sync, request, generation_params)

        loggers.framework.dev_debug(response)

        return response

    async def run_stream(
            self,
            request: AsyncIterator[DiarizationRequest],
            generation_params: DiarizationGenerationParams,
            **stream_settings_kwargs: Any
    ) -> AsyncGenerator[DiarizationResponse, None]:
        if request is None:
            raise ValueError("DiarizationRequest cannot be None")

        loop = asyncio.get_event_loop()

        async for chunk in request:
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(executor, self._sync, chunk, generation_params, stream_settings_kwargs)

            loggers.framework.dev_debug(response)

            yield response

    def _sync(
            self,
            request: DiarizationRequest,
            generation_params: DiarizationGenerationParams,
            stream_settings_kwargs: Optional[Dict[str, Any]] = None
    ) -> DiarizationResponse:
        load_dotenv()

        device = torch.device('cuda' if torch.cuda.is_available() and generation_params.device == 'cuda' else 'cpu')

        try:
            if generation_params.mode == 'detection':
                # model=Model(sample_rate=generation_params.sample_rate),  We could use this f we wanted to provide sample rate from frontend
                pipeline = VoiceActivityDetection(
                    segmentation=self.__class__.detection_model,
                    window=generation_params.window or 'sliding',
                    duration=generation_params.chunk_duration,
                    batch_size=generation_params.batch_size
                )
                pipeline.to(device)

                HYPER_PARAMETERS = {
                    # remove speech regions shorter than that many seconds.
                    "min_duration_on": generation_params.min_duration_on,
                    # fill non-speech regions shorter than that many seconds.
                    "min_duration_off": generation_params.min_duration_off
                }
                pipeline.instantiate(HYPER_PARAMETERS)

                with CreateWavFile(request, mime_type='audio/webm;codec=opus') as file_path:
                    annotation: Annotation = pipeline(file_path)
            else:
                pipeline = self.__class__.diarization_pipeline

                with CreateWavFile(request, mime_type='audio/webm;codec=opus') as file_path:
                    annotation: Annotation = pipeline(file_path)

                # dump the diarization output to disk using RTTM format
                with open("audio.rttm", "w") as rttm:
                    annotation.write_rttm(rttm)
        except Exception as e:
            raise e

        if not stream_settings_kwargs:
            stream_settings_kwargs = {}

        response: DiarizationResponse = self.converter.from_pyannote_annotation(annotation, generation_params, stream_settings_kwargs)

        return response
