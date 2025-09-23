import pytest
from unittest.mock import AsyncMock, MagicMock
from starlette.websockets import WebSocket
import src.websocket
from src.framework import Message
from src.websocket import WebSocketConnection, MessageWsEvents, WebSocketMessage


@pytest.fixture
def mock_websocket():
    mock = AsyncMock(spec=WebSocket)
    mock.accept = AsyncMock()
    return mock


@pytest.fixture
def mock_scenario():
    mock = AsyncMock()

    return mock


@pytest.fixture
def websocket_connection() -> WebSocketConnection:
    connection = WebSocketConnection(client_id="test_client_id", scenario_instance_id="test_scenario_instance_id")

    connection._wait_for_ready_event = AsyncMock()

    return connection


@pytest.fixture
def test_message() -> Message:
    return Message.from_ai(
        content="This is a test message",
        author_id="test_author_id",
        author_name="test_author_name",
        scenario_instance_id="test_scenario_instance_id"
    )


@pytest.mark.asyncio
class TestWebsocketConnection:

    async def test_create(self, websocket_connection, mock_websocket, mock_scenario):
        await websocket_connection.connect(mock_scenario, mock_websocket)

        mock_websocket.accept.assert_awaited_once()

    # async def test_send_message_async(self, websocket_connection, mock_websocket, mock_scenario, test_message):
    #     await websocket_connection.connect(mock_scenario, mock_websocket)
    #
    #     await websocket_connection.send_message_async(event=MessageWsEvents.FULL_MESSAGE, data=test_message)
    #
    #     expected_message = WebSocketMessage(event=MessageWsEvents.FULL_MESSAGE, data=test_message).model_dump()
    #
    #     mock_websocket.send_json.assert_awaited_with(expected_message)

