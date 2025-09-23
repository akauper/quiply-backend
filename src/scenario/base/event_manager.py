from typing import Dict, List, Callable, Coroutine, Any, TYPE_CHECKING

from src.utils import logger
from ..models import ScenarioEvent

if TYPE_CHECKING:
    from .scenario import Scenario


class EventManager:
    _listeners: Dict[ScenarioEvent, List[Callable[..., Coroutine[Any, Any, None]]]]

    def __init__(self) -> None:
        self._listeners = {event: [] for event in ScenarioEvent}

    def cleanup(self):
        self._listeners.clear()

    async def emit(self, event: ScenarioEvent, *args, **kwargs):
        if event in self._listeners:
            listeners = self._listeners[event]
            for listener in listeners:
                try:
                    await listener(*args, **kwargs)
                except Exception as e:
                    logger.debug(f"Listener failed with error: {e}")

    def subscribe(self, event: ScenarioEvent, listener: Callable[..., Coroutine[Any, Any, None]]):
        if not callable(listener):
            raise ValueError("Listener must be callable")

        self._listeners[event].append(listener)

    def unsubscribe(self, event: ScenarioEvent, listener: Callable[..., Coroutine[Any, Any, None]]):
        try:
            self._listeners[event].remove(listener)
        except ValueError:
            print(f"Listener not found for event: {event}")

    def has_event(self, event: ScenarioEvent) -> bool:
        return event in self._listeners
