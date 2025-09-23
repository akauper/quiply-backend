from .whisper import WhisperSttService
from .base_service import BaseSttService


def get_stt_service(name: str) -> BaseSttService:
    if name == "whisper":
        return WhisperSttService()
    else:
        raise NotImplementedError
