from typing import TypeVar, TYPE_CHECKING

from devtools import debug

from src.exceptions import BaseScenarioException, ScenarioUpdateException
from src.framework import Message, ModerationGenerator
from src.models import ScenarioResult, ScenarioAnalysis
from src.services import storage_service
# from src.websocket import WebSocketConnection, ScenarioWsEvents, ScenarioNotification, \
#     WebSocketMessage, MessageWsEvents
from src.websocket import WebSocketConnection, WebSocketMessage, PacketEventType
from .component import ScenarioComponent
from .component_manager import ComponentManager
from .voice_streaming import ScenarioVoiceStreaming
from ..._debug import quiply_debug

if TYPE_CHECKING:
    from .scenario import Scenario


TScenarioComponent = TypeVar("TScenarioComponent", bound=ScenarioComponent)


class LifecycleManager:
    scenario: 'Scenario'
    component_manager: ComponentManager
    moderation_generator: ModerationGenerator

    websocket_connection: WebSocketConnection
    voice_streaming: ScenarioVoiceStreaming

    def __init__(
            self,
            scenario: 'Scenario',
            component_manager: ComponentManager,
    ):
        self.scenario = scenario
        self.component_manager = component_manager
        self.moderation_generator = ModerationGenerator(process_id=scenario.instance_uid)

    def cleanup(self):
        self.moderation_generator.cleanup()
        del self.moderation_generator

    async def initialize(self, websocket_connection: WebSocketConnection) -> None:
        """Initializes the scenario and calls awake."""
        self.websocket_connection = websocket_connection
        self.websocket_connection.on_event(PacketEventType.MESSAGE, self._handle_user_websocket_message)

        self.voice_streaming = ScenarioVoiceStreaming(self.scenario, websocket_connection, self._handle_user_message)

        await self.component_manager.awake()
        self.scenario.logger.debug(f'Scenario {self.scenario.instance.uid} called awake successfully')

    async def start_scenario(self):
        """Called after ready message has been sent to client."""
        await self.component_manager.start()
        self.scenario.logger.debug(f'Scenario {self.scenario.instance.schema_id} ({self.scenario.instance.uid}) called start successfully')

        self.scenario.create_task(self._update_loop())
        self.scenario.logger.debug(f'Scenario {self.scenario.instance.schema_id} ({self.scenario.instance.uid}) created update loop task successfully')

        self.scenario.loggers.stage.info(f'Scenario {self.scenario.instance.schema_id} ({self.scenario.instance.uid}) fully initialized')

    async def _update_loop(self) -> None:
        while True:
            try:
                await self.component_manager.update()
            except BaseScenarioException as e:
                self.scenario.handle_exception(e.__class__, e, e.__traceback__)
            except Exception as e:
                self.scenario.handle_exception(ScenarioUpdateException, ScenarioUpdateException(e.args), e.__traceback__)

    async def end_scenario_async(self) -> ScenarioResult:
        self.scenario.loggers.stage.info(f'Ending scenario task for scenario instance {self.scenario.instance.uid} with client {self.scenario.user_uid}')
        if (debug_conversations := quiply_debug.get_conversations(self.scenario.template_uid)) is not None:
            conversations = debug_conversations
        else:
            conversations = self.scenario.component_manager.conversation_controller.conversations

        conversations = [conversation.prune_system_messages() for conversation in conversations]

        analysis: ScenarioAnalysis = await self.scenario.component_manager.analysis_engine.analyze_all_async(conversations)

        result: ScenarioResult = ScenarioResult(
            scenario_instance=self.scenario.instance,
            conversations=conversations,
            analysis=analysis,
        )
        # loggers.stage.warning(result.model_dump_json(indent=2))
        storage_service.create_scenario_result(result)
        return result

    def _handle_user_websocket_message(self, incoming_message: WebSocketMessage) -> None:
        user_message: Message = incoming_message.data
        if not user_message or user_message.role != 'user':
            return

        self.scenario.logger.warning(f'GOT USER MESSAGE: {incoming_message.data}')

        message = Message(
            created_at=user_message.created_at,
            content=user_message.content,
            author_id=self.scenario.account_data.id,
            author_name=self.scenario.users_name,
            scenario_instance_id=self.scenario.instance.uid,
            metadata=user_message.metadata,
        )
        self._handle_user_message(message)

    def _handle_user_message(self, message: Message) -> None:
        self.scenario.create_task(self._validate_user_message(message))

        if message.to_mentor:
            self.scenario.create_task(self.scenario.component_manager.step(message, True))
        else:
            self.scenario.create_task(self.scenario.component_manager.step(message, False))

    async def _validate_user_message(self, message: Message) -> None:
        """
        Validates the user message to check for injection. Run this in the background. It will exit the scenario if
        the message is an injection.
        """
        print('VALIDATION TURNED OFF')
        return

        response = await self.moderation_generator.run_async(message.content)
        if response.flagged:
            debug(response)
            # await self.websocket_connection.send_scenario_async(
            #     ScenarioWsEvents.NOTIFICATION,
            #     ScenarioNotification.SCENARIO_TERMINATED('You query violated Quiply terms of service.')
            # )
            self.websocket_connection.force_close()

    def on_agent_message(self, message: Message) -> None:
        self.scenario.create_task(self.component_manager.step(message, False))

    def on_advisor_message(self, message: Message) -> None:
        self.scenario.create_task(self.component_manager.step(message, True))
