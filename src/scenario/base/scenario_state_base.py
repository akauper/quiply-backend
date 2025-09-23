import asyncio
from abc import ABC
from typing import Coroutine, Any, List, Union

from src.framework import Message


class ScenarioStateObject(ABC):
    def cleanup(self):
        """Called when scenario is being cleaned up."""

    def defer_coroutine(self, coroutine: Union[Coroutine, List[Coroutine]]):
        """Defers a coroutine to be called at the end of the current lifecycle step (end of awake, start, step, etc)"""

    async def awake(self):
        """Called after websocket connection has been established but before ready event is sent."""

    async def start(self):
        """Called after scenario has sent ready message to client."""

    async def update(self, frame: int):
        """Called at a set real world time interval."""

    async def step(self, message: Message):
        """Called after every user or agent message is received/generated."""

    async def late_step(self, message: Message):
        """Called after all components and the scenario have called step"""

    async def step_mentor(self, message: Message):
        """Called after every user or advisor message is received/generated to/from the advisor."""

    async def late_step_mentor(self, message: Message):
        """Called after all components and the scenario have called step_advisor"""
