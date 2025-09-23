from typing import List, Optional

from pydantic import BaseModel, Field

from src.framework.models.base import UIDMixin, CreatedAtMixin
from .mode import DiarizationMode

SEGMENT_PRECISION: float = 1e-6


class DiarizationSegment(BaseModel):
    index: int
    """The index of this segment in the sequence of segments."""

    start_time: float = Field(default=0.0)
    """ The start time of this segment in seconds. """

    end_time: float = Field(default=0.0)
    """ The end time of this segment in seconds. """

    speaker: Optional[str] = Field(default=None)
    """ The label for the speaker of this segment. """

    is_final: bool = Field(default=False)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def valid(self) -> bool:
        return self.duration > SEGMENT_PRECISION


class DiarizationResponse(UIDMixin, CreatedAtMixin):

    mode: DiarizationMode
    """ Mode to use for inference. """

    segments: List[DiarizationSegment] = Field(default_factory=list)
    """ The list of segments in this diarization response. """

    duration: float = Field(default=0.0)
    """ The duration of the audio in seconds. It is possible to have 0 segments with a duration > 0.
    This can happen when the diarization model is not able to detect any speakers in the audio. """

    @property
    def valid(self) -> bool:
        return self.duration > SEGMENT_PRECISION * len(self.segments)

    @property
    def speakers(self) -> List[str]:
        return list(set([segment.speaker for segment in self.segments]))

    @property
    def speaker_count(self) -> int:
        return len(self.speakers)
