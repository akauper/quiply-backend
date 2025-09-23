import asyncio
from typing import List, Coroutine, Any, Union, Optional


class AsyncObject:
    """
    Manages asynchronous tasks within the application, ensuring that all tasks are properly canceled and cleaned up
    when the AsyncObject is no longer needed.
    """

    _async_tasks: List[asyncio.Task]
    """List of tasks"""

    def __init__(self):
        self._async_tasks: List[asyncio.Task] = []

    def cleanup(self):
        for task in self._async_tasks:
            task.cancel()

        self._async_tasks.clear()

    async def cleanup_async(self):
        """Cancel all tracked tasks and wait for them to finish."""
        for task in self._async_tasks:
            task.cancel()

        await asyncio.gather(*self._async_tasks, return_exceptions=True)
        self._async_tasks.clear()

    @staticmethod
    async def _gather_coroutines(coroutines: List[Coroutine[Any, Any, Any]]):
        await asyncio.gather(*coroutines)

    def create_task(
            self,
            coroutine: Union[Coroutine[Any, Any, Any], List[Coroutine[Any, Any, Any]]],
            *,
            delay: Optional[float] = None
    ) -> asyncio.Task:
        """Start an async task and add it to the task list."""

        if delay is None:
            return self._create_task_sync(coroutine)
        else:
            return asyncio.create_task(self._create_task_async(coroutine, delay))

    async def _create_task_async(
            self,
            coroutine: Union[Coroutine[Any, Any, Any], List[Coroutine[Any, Any, Any]]],
            delay: float
    ) -> asyncio.Task:
        await asyncio.sleep(delay)
        return self._create_task_sync(coroutine)

    def _create_task_sync(
            self,
            coroutine: Union[Coroutine[Any, Any, Any], List[Coroutine[Any, Any, Any]]],
    ) -> asyncio.Task:
        if isinstance(coroutine, list):
            task = asyncio.create_task(self._gather_coroutines(coroutine))
        else:
            task = asyncio.create_task(coroutine)

        self._async_tasks.append(task)

        return task
