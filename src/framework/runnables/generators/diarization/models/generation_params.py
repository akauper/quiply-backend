from typing import Literal, Optional

from pydantic import BaseModel, Field

from .mode import DiarizationMode


class DiarizationGenerationParams(BaseModel):
    """
    Parameters for generating diarization from a service.
    """

    device: Literal['cuda', 'cpu'] = Field(default='cpu')
    """ Device to use for inference. """

    mode: DiarizationMode = Field(default='detection')
    """ Mode to use for inference. """

    min_duration_on: float = Field(default=0.0)
    """ Remove speech regions shorter than this many seconds. """

    min_duration_off: float = Field(default=0.0)
    """ Fill non-speech regions shorter than this many seconds. """

    window: Optional[Literal['sliding', 'whole']] = Field(default=None)
    """ Use a "sliding" window and aggregate the corresponding outputs (default)
    or just one (potentially long) window covering the "whole" file or chunk. """

    chunk_duration: Optional[float] = Field(default=None)
    """ Chunk duration, in seconds. Defaults to duration used for training the model.
    Has no effect when `window` is "whole". """

    batch_size: Optional[int] = Field(default=32)
    """ Larger values (should) make inference faster. Defaults to 32 """
