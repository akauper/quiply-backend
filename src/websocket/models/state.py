from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field


class WebSocketStatus(str, Enum):
    GetScenario = 'get_scenario'
    AcceptConnection = 'accept_connection'
    WaitForReadyEvent = 'wait_for_ready_event'
    SendReadyEvent = 'send_ready_event'
    InitializeScenario = 'initialize_scenario'
    ScenarioRunning = 'scenario_running'


class QWebSocketState(BaseModel):
    status: WebSocketStatus = Field(default=WebSocketStatus.GetScenario)
    ready_message: Optional[str] = Field(default=None)
    error: Optional[Any] = Field(default=None)
    last_ping_time: Optional[float] = Field(default=None)
    last_pong_time: Optional[float] = Field(default=None)

