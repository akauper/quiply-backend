from enum import Enum
from typing import Union


class DebugWsEvents(str, Enum):
    DEBUG_GENERATE_RESPONSE = 'debug_generate_response'


DebugWsDataTypes = Union[str, None]