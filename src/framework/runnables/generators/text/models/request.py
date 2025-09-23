from typing import Union, List

from src.framework.models.message import Message

TextGenerationRequest = Union[
    Message,
    List[Message],
    str,
]
