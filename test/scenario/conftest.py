from unittest.mock import Mock, AsyncMock, MagicMock

import pytest

from src.scenario import Scenario
from src.websocket import WebSocketConnection


@pytest.fixture
def mock_websocket_connection():
    mock = MagicMock(spec=WebSocketConnection)

    mock.create_connection_task = MagicMock()
    mock.create_message_task = MagicMock()
    mock.create_scenario_task = MagicMock()
    mock.create_base_task = MagicMock()

    mock.send_connection_async = AsyncMock()
    mock.send_message_async = AsyncMock()
    mock.send_scenario_async = AsyncMock()
    mock.send_base_async = AsyncMock()

    return mock


@pytest.fixture
def mock_scenario(mock_scenario_instance, mock_scenario_template, mock_websocket_connection) -> Mock:
    mock = MagicMock(spec=Scenario)

    mock.scenario_instance = mock_scenario_instance
    mock.scenario_template = mock_scenario_template
    mock.websocket_connection = mock_websocket_connection

    return mock
