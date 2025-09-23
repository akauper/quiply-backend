from typing import Any, Dict, Optional

from pyannote.core.annotation import Annotation

from src.framework.exceptions import ConversionException
from ...models import DiarizationGenerationParams, DiarizationSegment, DiarizationResponse


class PyannoteSpeechDiarizationConverter:
    """
    A class for converting between Quiply and Pyannote speech diarization objects.

    :raises ConversionException: If the conversion fails.
    """

    @staticmethod
    def from_pyannote_annotation(
            annotation: Annotation,
            generation_params: DiarizationGenerationParams,
            stream_settings: Optional[Dict[str, Any]] = None
    ) -> DiarizationResponse:
        """
        Convert a Pyannote Annotation to a Quiply DiarizationResponse.

        :param annotation: The Pyannote Annotation to convert.
        :param generation_params: The generation parameters used to generate the annotation.
        :param stream_settings: The stream settings used to generate the annotation.
        :return: The converted Quiply DiarizationResponse.
        """
        try:
            segments = []

            for turn, _, speaker in annotation.itertracks(yield_label=True):
                segment = DiarizationSegment(
                    index=len(segments),
                    start_time=turn.start,
                    end_time=turn.end,
                    speaker=speaker or None
                )
                segments.append(segment)

            if len(segments) > 0:
                segments[-1].is_final = True

            duration = 0.0
            if len(segments) > 0:
                duration = segments[-1].end_time
            elif stream_settings and stream_settings.get('chunk_timeslice', None):
                duration = stream_settings['chunk_timeslice']

            return DiarizationResponse(
                mode=generation_params.mode,
                segments=segments,
                duration=duration
            )
        except Exception as e:
            raise ConversionException(
                PyannoteSpeechDiarizationConverter,
                from_type=Annotation,
                to_type=DiarizationResponse,
                inner_exception=e
            )