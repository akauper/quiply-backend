from typing import Any

from .base import BaseQuiplyException
from ..websocket.models import WebSocketStatus, WebSocketMessage
from .scenario import BaseScenarioException


class BaseWebsocketException(BaseQuiplyException):
    """Base exception for WebSocket related errors."""
    stage: WebSocketStatus
    inner: BaseException

    def __init__(self, stage: WebSocketStatus, message: str = None, inner: BaseException = None):
        if message is None:
            message = f"A WebSocket error occurred at stage '{stage.name}'"
        if inner:
            message += f" (Inner exception - {type(inner)}: {inner})"
        super().__init__(message)
        self.stage = stage
        self.inner = inner


class WebsocketTimeoutException(BaseWebsocketException):
    """Exception for timeouts occurring in WebSocket operations."""


class WebsocketScenarioNotFoundException(BaseWebsocketException):
    """Exception raised when a WebSocket scenario is not found."""


class WebsocketInitializeScenarioException(BaseWebsocketException):
    """Exception raised when a WebSocket scenario fails to initialize."""

    def __init__(self, scenario_exception: BaseScenarioException, message: str = None):
        super().__init__(stage=WebSocketStatus.InitializeScenario, message=message, inner=scenario_exception)
        self.scenario_exception = scenario_exception


class WebsocketReceiveException(BaseWebsocketException):
    """Exception raised when a WebSocket fails to receive a message."""

    def __init__(self, inner: BaseException, data: Any = None):
        super().__init__(
            stage=WebSocketStatus.ScenarioRunning,
            message=f"An unexpected exception occurred while receiving a message from the WebSocket connection. Exception: {inner} Data: {data if data else 'NO_DATA'}",
            inner=inner
        )


class WebsocketHandleMessageException(WebsocketReceiveException):
    """Exception raised when a WebSocket fails to handle a message."""

    def __init__(self, inner: BaseException, data: WebSocketMessage):
        super().__init__(
            inner=inner,
            data=data
        )