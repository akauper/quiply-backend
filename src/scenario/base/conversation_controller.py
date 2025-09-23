import asyncio
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, TYPE_CHECKING, Literal, Optional

from framework import framework_settings
from src.settings import quiply_settings
from src.framework import (
    TextGenerator,
    Message,
    Conversation,
    TextGenerationParams,
    MessageRole,
)
# from src.websocket import ScenarioWsEvents, ScenarioNotification
from .component import ScenarioComponent
from ..agents.scenario_agent import ScenarioAgent
from ..models import TScenarioStage, ScenarioEvent, AgentType
from ..util import str_to_message_list

if TYPE_CHECKING:
    from .scenario import Scenario


class FirstSpeakerMode(str, Enum):
    USER = "user"
    AI = "ai"
    RANDOM = "random"


class ConversationController(ScenarioComponent, ABC):
    current_speaking_agent: ScenarioAgent
    first_speaker: Literal["user", "ai"]

    separate_agent_conversations: bool

    def __init__(
        self,
        scenario: "Scenario",
    ) -> None:
        super().__init__(scenario, priority=0)

        self.separate_agent_conversations = False

        self.scenario.event_manager.subscribe(
            ScenarioEvent.ON_STAGE_CHANGE, self.on_stage_change
        )

        if self.first_speaker_mode == FirstSpeakerMode.USER:
            self.first_speaker = "user"
        elif self.first_speaker_mode == FirstSpeakerMode.AI:
            self.first_speaker = "ai"
        else:
            self.first_speaker = "user" if random.randint(0, 1) == 0 else "ai"

    def cleanup(self):
        if hasattr(self, "current_speaking_agent"):
            del self.current_speaking_agent

        super().cleanup()

    async def start(self):
        self.current_speaking_agent = self.scenario.agents[0]

        # Anthropic requires an initial user message to start the conversation
        if framework_settings.runnables.generators.text.service_name == "anthropic":
            for agent in self.scenario.agents:
                agent.add_message(Message(role=MessageRole.user, content="Start the Conversation"))

        self._add_initial_template_messages()
        self._init_debug_conversations()

        await self.calculate_next_speaking_agent_async()
        self.send_first_message()

    def _init_debug_conversations(self) -> None:
        debug_conversation = self.scenario_config.debug_starting_conversation
        if debug_conversation is None:
            return

        messages = str_to_message_list(
            message_str=debug_conversation,
            agents=self.scenario.agents,
            users_name=self.scenario.users_name,
            users_uid=self.scenario_instance.user_id,
            scenario_instance_uid=self.scenario_instance.uid,
        )

        for agent in self.scenario.agents:
            agent.add_message(messages)

    def _add_initial_template_messages(self) -> None:
        return
        initial_messages = self.scenario_template.initial_messages
        if initial_messages is None:
            return

        messages: List[Message] = []
        for message_template in initial_messages:
            if message_template.author_type == "user":
                messages.append(
                    Message.from_user(
                        content=message_template.content,
                        author_id=self.scenario_instance.user_id,
                        author_name=self.scenario.users_name,
                        scenario_instance_id=self.scenario_instance.uid,
                    )
                )
            else:
                agent = self.scenario.agents[0]
                messages.append(
                    Message.from_ai(
                        content=message_template.content,
                        author_id=agent.template.uid,
                        author_name=agent.name,
                        scenario_instance_id=self.scenario_instance.uid,
                    )
                )

        for agent in self.scenario.agents:
            agent.add_message(messages)

    def send_first_message(self):
        if self.first_speaker == "user":
            pass
            # self.websocket_connection.create_scenario_task(
            #     ScenarioWsEvents.NOTIFICATION,
            #     data=ScenarioNotification.AWAIT_USER_MESSAGE(),
            # )
        else:
            self.generate_agent_message(random.choice(self.scenario.agents))

    async def step(self, message: Message):
        await self.calculate_next_speaking_agent_async()

        if self.separate_agent_conversations:
            if message.is_from(MessageRole.user):
                self.current_speaking_agent.add_message(message)
        else:
            for agent in self.scenario.agents:
                if agent.template.uid != message.author_id:
                    agent.add_message(message)

    async def step_mentor(self, message: Message):
        if message.is_from(MessageRole.user):
            self.scenario.mentor.add_message(message)

    async def late_step(self, message: Message):
        if message.is_from(MessageRole.user):
            self.generate_agent_message()  # We dont need to provide the user message. it was already saved to memory in step()

    async def late_step_mentor(self, message: Message):
        if message.is_from(MessageRole.user):
            self.generate_mentor_message()

    def on_stage_change(self, stage: TScenarioStage):
        # Send our first stage message
        if stage.first_speaker_type == "user":
            pass
            # self.websocket_connection.create_scenario_task(
            #     ScenarioWsEvents.NOTIFICATION,
            #     data=ScenarioNotification.AWAIT_USER_MESSAGE(),
            # )
        else:
            self.generate_agent_message(
                self.scenario.agents[stage.first_speaker_agent_index]
            )

    @property
    @abstractmethod
    def first_speaker_mode(self) -> FirstSpeakerMode:
        """Determines who sends the first message in the conversation"""

    @abstractmethod
    async def calculate_next_speaking_agent_async(self) -> ScenarioAgent:
        pass

    @property
    def conversations(self) -> List[Conversation]:
        return [agent.full_conversation for agent in self.scenario.agents]

    @property
    def current_conversation(self) -> Conversation:
        return self.current_speaking_agent.full_conversation

    def generate_agent_message(self, agent: Optional[ScenarioAgent] = None):
        if quiply_settings.evaluation.enabled:
            import inspect

            outer_stack = inspect.stack()  # We need to pass the outer stack for correct tracing since we are using async
        else:
            outer_stack = None

        agent = agent or self.current_speaking_agent

        event_loop = asyncio.get_event_loop()
        # print(event_loop)

        if self.scenario.settings.message_mode == "stream" and agent.type != AgentType.MENTOR:
            self.create_task(agent.run_async_stream())
        elif self.scenario.settings.message_mode == "async" or agent.type == AgentType.MENTOR:
            self.create_task(agent.run_async())
        else:
            raise Exception(
                f"Invalid message mode: {quiply_settings.scenario.message_mode}"
            )

    def generate_mentor_message(self, user_message: Optional[Message] = None):
        print("generate mentor message")
        self.generate_agent_message(agent=self.scenario.mentor)

    async def generate_debug_response_async(self) -> str:
        try:
            text_generator = TextGenerator(
                process_id=self.instance_uid,
                generation_params=TextGenerationParams(temperature=1),
            )

            request: List[Message] = [
                Message.from_system(
                    content="Respond Concisely. Disagree with the last thing said, no matter what was said."
                ),
            ]
            for m in self.current_speaking_agent.full_conversation.messages:
                if not m.is_from(MessageRole.system):
                    request.append(m)

            response = await text_generator.run_async(request)
        except Exception as e:
            self.logger.exception(e)
            raise e

        return response.content
