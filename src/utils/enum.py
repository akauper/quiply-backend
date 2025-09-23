from enum import Enum
from typing import Type


def enum_contains_value(enum_class: Type[Enum], value: str) -> bool:
    return any(value == item.value for item in enum_class)
