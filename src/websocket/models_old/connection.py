from enum import Enum
from typing import Union


class ConnectionWsEvents(str, Enum):
    READY = 'ready'
    ERROR = 'error'
    DISCONNECT = 'disconnect'
    PING = 'ping'
    PONG = 'pong'


ConnectionWsDataTypes = Union[str, None]
