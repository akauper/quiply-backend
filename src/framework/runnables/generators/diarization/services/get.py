from typing import TypeVar

from .base import BaseSpeechDiarizationService

TSpeechDiarizationService = TypeVar('TSpeechDiarizationService', bound=BaseSpeechDiarizationService)


def get_speech_diarization_service(service_name: str) -> TSpeechDiarizationService:
    if service_name == 'pyannote':
        from .pyannote import PyannoteSpeechDiarizationService
        return PyannoteSpeechDiarizationService()
    raise NotImplementedError(f'Speech Diarization service: {service_name} is not implemented')
