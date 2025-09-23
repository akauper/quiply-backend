import logging
from enum import Enum
from uuid import UUID, uuid4, uuid5
from .string_manipulation import *
from .logging import logger, loggers
from .files import *
from .enum import *

# logger = logging.getLogger(__name__)


NAMESPACE = UUID('1e8be8e5-dbe4-49ac-85ca-3543c96ecdd6')


def create_uuid(seed: str = None):
    if seed:
        return str(uuid5(NAMESPACE, seed))
    else:
        return str(uuid4())


def enum_contains(cls: Enum, enum_name: str):
    return hasattr(cls, enum_name)



