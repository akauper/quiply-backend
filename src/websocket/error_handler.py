from types import TracebackType
from typing import Optional, Type

from starlette.websockets import WebSocket, WebSocketState

from src.exceptions import BaseWebsocketException, WebsocketTimeoutException, WebsocketScenarioNotFoundException, \
    WebsocketInitializeScenarioException, WebsocketReceiveException
# from .models import WebSocketMessage, ScenarioWsEvents, ScenarioNotification
from .models import WebSocketMessage, ScenarioEventType
from src.utils import logger


async def handle_websocket_exception(
        websocket: WebSocket,
        exc_type: Optional[Type[BaseWebsocketException]] = None,
        exc_val: Optional[BaseWebsocketException] = None,
        exc_tb: Optional[TracebackType] = None
):
    logger.exception(f"An exception of type {exc_type} occurred with value {exc_val}")

    try:
        if exc_type is WebsocketTimeoutException:
            await send_connection_closed_message(websocket, 'The WebSocket connection timed out.')
            await websocket.close(code=1008, reason=exc_val)
        elif exc_type is WebsocketScenarioNotFoundException:
            await send_connection_closed_message(websocket, 'The requested scenario was not found.')
            await websocket.close(code=4001, reason=exc_val)
        elif exc_type is WebsocketInitializeScenarioException:
            await send_connection_closed_message(websocket, 'The requested scenario failed to initialize.')
            await websocket.close(code=1002, reason=exc_val)
        elif exc_type is WebsocketReceiveException:
            await send_connection_closed_message(websocket, 'An error occurred while receiving a message.')
            await websocket.close(code=1003, reason=exc_val)
        else:
            await send_connection_closed_message(websocket, 'An unknown error occurred.')
            await websocket.close(code=1011, reason=exc_val)
    except Exception as e:
        pass


async def send_connection_closed_message(
        websocket: WebSocket,
        message: Optional[str] = None
):
    if websocket.application_state != WebSocketState.CONNECTED or websocket.client_state != WebSocketState.CONNECTED:
        return

    try:
        pass
        # message: WebSocketMessage = WebSocketMessage(
        #     event=ScenarioEventType.NOTIFICATION,
        #     data=ScenarioNotification.CONNECTION_ERROR(message)
        # )
        # dump = message.model_dump(exclude_unset=False)
        # await websocket.send_json(dump)
    except Exception as e:
        logger.exception(f"Error sending connection closed message: {e}")
