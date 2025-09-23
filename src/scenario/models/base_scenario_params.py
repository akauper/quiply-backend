from abc import ABC
from typing import Optional, List

from pydantic import BaseModel, Field


class BaseScenarioParams(ABC, BaseModel):
    actor_ids: List[str] = Field(default_factory=list[str])

    class Config:
        extra = 'allow'
