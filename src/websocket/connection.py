import asyncio
import json
import time
from types import TracebackType
from typing import Dict, Optional, TYPE_CHECKING, Type, Callable, List

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from src.async_object import AsyncObject
from src.settings import quiply_settings
from src.exceptions import (
    WebsocketTimeoutException,
    BaseWebsocketException,
    BaseScenarioException,
    WebsocketInitializeScenarioException,
    WebsocketReceiveException,
    WebsocketHandleMessageException,
)
from src.framework import Message
from src.models.voice import VoiceStream, VoiceChunk
from src.utils import enum_contains_value
from .error_handler import handle_websocket_exception
from .models import (
    WebSocketEvent,
    WebSocketEventType,
    WebSocketMessage,
    ConnectionEventType,
    ScenarioEventType,
    ConnectionEvent,
    ScenarioEvent,
    WebSocketStatus,
    PacketEventType,
    PacketEvent,
    VoiceEventType,
    VoiceEvent,
)

if TYPE_CHECKING:
    from src.scenario import Scenario
    from src.scenario.util import ScenarioWebsocketLogger


class WebSocketConnection(AsyncObject):
    _client_id: str
    _scenario_instance_id: str

    _force_closed: bool
    _websocket: WebSocket
    _scenario: "Scenario"
    logger: "ScenarioWebsocketLogger"

    _event_subscribers: Dict[
        WebSocketEventType, List[Callable[[WebSocketMessage], None]]
    ]

    _voice_streams: Dict[str, VoiceStream]
    _voice_stream_subscribers: List[Callable[[VoiceStream], None]]

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseWebsocketException]],
        exc_val: Optional[BaseWebsocketException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        from src.scenario import scenario_manager

        if exc_type is not None:
            await handle_websocket_exception(self._websocket, exc_type, exc_val, exc_tb)
        else:
            if (
                self._websocket.application_state == WebSocketState.CONNECTED
                and self._websocket.client_state == WebSocketState.CONNECTED
            ):
                await self._websocket.close(code=1000, reason="Normal closure")

        await self.cleanup_async()
        scenario_manager.destroy_scenario(self._scenario_instance_id)

        return True

    def __init__(self, client_id: str, scenario_instance_id: str) -> None:
        super().__init__()
        self._client_id = client_id
        self._scenario_instance_id = scenario_instance_id

        self._event_subscribers = {}
        self._force_closed = False

        self._voice_streams = {}
        self._voice_stream_subscribers = []

    async def cleanup_async(self):
        self._event_subscribers.clear()

        if hasattr(self, "_scenario"):
            del self._scenario
        await super().cleanup_async()

    def force_close(self):
        self._force_closed = True
        self._websocket.close()

    async def connect(self, scenario: "Scenario", websocket: WebSocket):
        """Connect to the WebSocket and initialize the scenario"""
        self._scenario = scenario
        self._websocket = websocket
        self.logger = scenario.loggers.websocket

        try:
            await asyncio.wait_for(
                self._websocket.accept(),
                timeout=quiply_settings.websocket.accept_timeout,
            )
        except asyncio.TimeoutError as e:
            raise WebsocketTimeoutException(
                stage=WebSocketStatus.AcceptConnection, inner=e
            )
        except Exception as e:
            raise BaseWebsocketException(WebSocketStatus.AcceptConnection, inner=e)

        try:
            self.logger.debug(
                f"Waiting for client [{self._client_id}] to send ready event"
            )
            await asyncio.wait_for(
                self._wait_for_ready_event(),
                timeout=quiply_settings.websocket.ready_event_timeout,
            )
        except asyncio.TimeoutError as e:
            raise WebsocketTimeoutException(
                stage=WebSocketStatus.WaitForReadyEvent, inner=e
            )
        except Exception as e:
            raise BaseWebsocketException(
                stage=WebSocketStatus.WaitForReadyEvent, inner=e
            )

        try:
            self.logger.debug(
                f"Initializing scenario [{self._scenario.template_uid}] for client [{self._client_id}]"
            )
            await self._scenario.lifecycle_manager.initialize(self)
        except BaseScenarioException as e:
            raise WebsocketInitializeScenarioException(e)
        except Exception as e:
            raise BaseWebsocketException(
                stage=WebSocketStatus.InitializeScenario, inner=e
            )

        try:
            self.logger.debug(f"Sending ready event to client [{self._client_id}]")
            await self._send_ready_event()
        except Exception as e:
            raise BaseWebsocketException(stage=WebSocketStatus.SendReadyEvent, inner=e)

        try:
            self.logger.debug(
                f"Starting scenario [{self._scenario.template_uid}] for client [{self._client_id}]"
            )
            await self._scenario.lifecycle_manager.start_scenario()
        except BaseScenarioException as e:
            raise WebsocketInitializeScenarioException(e)
        except Exception as e:
            raise BaseWebsocketException(
                stage=WebSocketStatus.InitializeScenario, inner=e
            )

        self.logger.debug(
            f"WebsocketConnection connect complete for client [{self._client_id}] with scenario [{self._scenario.template_uid}]"
        )

    async def _wait_for_ready_event(self):
        while True:
            data = await self._websocket.receive_text()
            data_dict = json.loads(data)
            incoming_message = WebSocketMessage.model_validate(data_dict)
            if incoming_message.type == ConnectionEventType.READY:
                break
            else:
                self.logger.warning(
                    f"Unexpected event received while waiting for ready event: {incoming_message}"
                )

    async def _send_ready_event(self):
        await self._websocket.send_json(
            {
                "type": ConnectionEventType.READY,
                "data": self._scenario.get_initializing_message(),
            }
        )

    async def listen(self):
        """Loop to listen for incoming messages from the client. This keeps the entire scenario loop running."""

        while (
            self._websocket.client_state is WebSocketState.CONNECTED
            and not self._force_closed
        ):
            # self.logger.debug(f'Client {self._client_id} listening')
            data = None

            try:
                # Receive the message (could be bytes or text)
                ws_message = await self._websocket.receive()
            except Exception as e:
                raise WebsocketReceiveException(inner=e)

            try:
                if "text" in ws_message:
                    data = ws_message[
                        "text"
                    ].encode()  # convert to bytes for uniformity
                    data_dict = json.loads(data.decode("utf-8"))

                    if data_dict["type"] != "voice_chunk":
                        self.logger.warning(
                            f"Received message from WebSocket: {data_dict}"
                        )

                    if data_dict["type"] == "typing_start":
                        continue

                    if data_dict.get("data"):
                        data_dict["data"] = self.validate_data(data_dict)

                    incoming_message = WebSocketMessage.model_validate(data_dict)

                    if enum_contains_value(VoiceEventType, incoming_message.type):
                        self._handle_voice_message(incoming_message)
                    elif incoming_message.requires_response:
                        self._handle_requires_response_message(incoming_message)
                    else:
                        self._handle_message(incoming_message)
                    # if incoming_message.requires_response:
                    #     self._handle_requires_response_message(incoming_message)
                    # else:
                    #     self._handle_message(incoming_message)
                else:
                    self.logger.warning(
                        f"Unexpected message format (not text) received in WebSocket: {ws_message}"
                    )
                    continue

            except WebSocketDisconnect:
                break
            except Exception as e:
                """Trap the exception here so an incoming message doesnt end the connection"""
                self.logger.exception(WebsocketReceiveException(inner=e, data=data))

    @staticmethod
    def validate_data(data_dict):
        data = data_dict["data"]

        if data_dict["type"] == PacketEventType.MESSAGE:
            return Message(**data)
        # elif enum_contains_value(VoiceEventType, data_dict['event']):
        #     return VoiceChunk.model_validate(data)
        return data

    def _handle_message(self, incoming_message: WebSocketMessage):
        try:
            event_type = incoming_message.type
            self.logger.debug(f"Received message: {incoming_message}")
            if event_type in self._event_subscribers:
                for callback in self._event_subscribers[event_type]:
                    callback(incoming_message)
            else:
                self.logger.warning(f"Unhandled event: {event_type}")
        except Exception as e:
            raise WebsocketHandleMessageException(inner=e, data=incoming_message)

    def _handle_voice_message(self, incoming_message: WebSocketMessage):
        chunk: VoiceChunk = VoiceChunk.model_validate(incoming_message.data)

        if incoming_message.type == VoiceEventType.VOICE_CHUNK:
            if chunk.is_start:
                voice_stream = VoiceStream(chunk.stream_id, chunk.settings)
                self._voice_streams[chunk.stream_id] = voice_stream

                voice_stream.on_end(self._on_stream_end)

                self.logger.info(f"Voice stream started: {chunk.stream_id}")

                for callback in self._voice_stream_subscribers:
                    callback(self._voice_streams[chunk.stream_id])

            self._voice_streams[chunk.stream_id].add_chunk(chunk)
        elif incoming_message.type == VoiceEventType.VOICE_END:
            if chunk.stream_id in self._voice_streams:
                self._voice_streams[chunk.stream_id].add_chunk(chunk)
            else:
                self.logger.warning(
                    f"Got Voice End event for stream {chunk.stream_id} that does not exist"
                )
        elif incoming_message.type == VoiceEventType.VOICE_ERROR:
            if chunk.stream_id in self._voice_streams:
                self._voice_streams[chunk.stream_id].add_chunk(chunk)
            else:
                self.logger.warning(
                    f"Got Voice Error event for stream {chunk.stream_id} that does not exist"
                )
        else:
            self.logger.error(f"Unhandled voice event: {incoming_message}")

    def _on_stream_end(self, stream_id: str):
        if stream_id in self._voice_streams:
            self._voice_streams[stream_id].off_end(self._on_stream_end)
            self._voice_streams.pop(stream_id)

    async def _handle_debug_generate_response(
        self, websocket_message: WebSocketMessage
    ):
        """Need a separate method for this, so we can create a task rather than holding up the listen loop"""

        self.logger.debug(
            f"Handling debug_generate_response message: {websocket_message}"
        )

        websocket_message.data = (
            await self._scenario.conversation_controller.generate_debug_response_async()
        )

        self.logger.debug(f"Generated Debug response: {websocket_message.data}")

        await self._websocket.send_json(websocket_message.model_dump())

    def _handle_requires_response_message(self, incoming_message: WebSocketMessage):
        try:
            self.logger.debug(f"Handling requires_response message: {incoming_message}")

            event_type = incoming_message.type

            websocket_message = WebSocketMessage(
                uid=incoming_message.uid,
                type=incoming_message.type,
            )

            if event_type == ConnectionEventType.PING:
                websocket_message.type = ConnectionEventType.PONG
                websocket_message.data = str(time.time())
            elif event_type == ScenarioEventType.ADVANCE_STAGE:
                self.create_task(self._scenario.stage_manager.advance_stage_async())
            # elif event_type == DebugEventType.DEBUG_GENERATE_RESPONSE:
            #     self.create_task(self._handle_debug_generate_response(websocket_message))
            #     return

            print("sending requires_response", websocket_message)
            self.create_task(self._websocket.send_json(websocket_message.model_dump()))
        except Exception as e:
            raise WebsocketHandleMessageException(inner=e, data=incoming_message)

    def on_event(
        self,
        event_type: WebSocketEventType,
        callback: Callable[[WebSocketMessage], None],
    ):
        if event_type not in self._event_subscribers:
            self._event_subscribers[event_type] = []
        self._event_subscribers[event_type].append(callback)

    def off_event(
        self,
        event_type: WebSocketEventType,
        callback: Callable[[WebSocketMessage], None],
    ):
        if event_type in self._event_subscribers:
            self._event_subscribers[event_type].remove(callback)

    def on_voice_stream_start(self, callback: Callable[[VoiceStream], None]):
        self._voice_stream_subscribers.append(callback)

    def off_voice_stream_start(self, callback: Callable[[VoiceStream], None]):
        self._voice_stream_subscribers.remove(callback)

    @property
    def _check_is_connected(self) -> bool:
        if (
            self._websocket.application_state != WebSocketState.CONNECTED
            or self._websocket.client_state != WebSocketState.CONNECTED
        ):
            self.logger.error(f"Client {self._client_id} is not connected")
            return False
        return True

    def create_send_task(self, event: WebSocketEvent) -> asyncio.Task:
        return self.create_task(self.send_async(event))

    async def send_async(self, event: WebSocketEvent) -> None:
        if not self._check_is_connected:
            return

        try:
            message = WebSocketMessage(type=event.type, data=event.data)
            # print("send_to_client:")
            # print(message)
        except Exception as e:
            self.logger.exception(f"Error while creating WebSocket message: {e}")
            return

        try:
            dump = message.model_dump(exclude_unset=False)
            await self._websocket.send_json(dump)
        except Exception as e:
            self.logger.exception(
                f"Exception while sending WebSocket message: {e}  ---- {message}"
            )
        self._handle_websocket_message_sent(message)

    def _handle_websocket_message_sent(self, websocket_message: WebSocketMessage):
        pass
