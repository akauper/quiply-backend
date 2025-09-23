import json

import websockets
from websockets import WebSocketClientProtocol

from src.utils import loggers
from src.websocket import MessageWsEvents
from src.websocket.models import WebSocketMessage, ConnectionWsEvents
from src.framework.models import Message, MessageRole


class AutoScenarioWebSocketClient:
    def __init__(self, client_id: str, scenario_instance_id: str):
        self.client_id = client_id
        self.scenario_instance_id = scenario_instance_id
        self.websocket: WebSocketClientProtocol | None = None
        self.ready_message = None

    async def connect(self):
        url = f"ws://localhost:5005/ws/{self.client_id}/{self.scenario_instance_id}"
        self.websocket = await websockets.connect(url)
        loggers.evaluation.info(f"Connected to {url}")

        await self.send_message(WebSocketMessage(event=ConnectionWsEvents.READY))
        await self.handle_messages()

    async def send_message(self, message: WebSocketMessage):
        if self.websocket:
            await self.websocket.send(message.model_dump_json())
            loggers.evaluation.info(f"Sent message: {message}")
        else:
            loggers.evaluation.error("WebSocket connection is not established.")

    async def send_user_message(self, content: str | Message) -> Message:
        if isinstance(content, Message):
            message = content
        else:
            message = Message(
                role=MessageRole.user,
                content=content,
                author_id=self.client_id,
                scenario_instance_id=self.scenario_instance_id,
            )
        await self.send_message(WebSocketMessage(event=MessageWsEvents.USER_MESSAGE, data=message))
        return message

    async def handle_messages(self):
        if self.websocket:
            async for message in self.websocket:
                loggers.evaluation.info(f"Received message: {message}")
                parsed_message = json.loads(message)
                if parsed_message["event"] == "ready":
                    self.ready_message = parsed_message.get("data")
                    loggers.evaluation.info(f"Got Ready: {self.ready_message}")
                    break
                # elif parsed_message["event"] == "full_message":
                #
        else:
            loggers.evaluation.error("WebSocket connection is not established.")

    async def wait_for_ai_message(self) -> Message:
        if self.websocket:
            print("Waiting for AI message...")
            async for message in self.websocket:
                loggers.evaluation.info(f"Received message: {message}")
                parsed_message = json.loads(message)
                if parsed_message["event"] == "full_message":
                    data = parsed_message.get("data")
                    return Message.model_validate(data)
        else:
            loggers.evaluation.error("WebSocket connection is not established.")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            loggers.evaluation.info("WebSocket connection closed.")
