import random
from abc import ABC, abstractmethod
from typing import List, Generic, Literal, TYPE_CHECKING, Optional

from devtools import debug

from src._debug import quiply_debug
from src.models import EventMessage
# from src.websocket import ScenarioWsEvents, ScenarioNotification, MessageWsEvents
from .component import ScenarioComponent
from ..models import TScenarioStage, ScenarioEvent, StageFirstSpeakerMode, \
    ScenarioStage, ScenarioAssessment, ScenarioProgress
from src.framework import Message, MessageRole, prompts, TextGenerator, TextGenerationParams, Conversation

if TYPE_CHECKING:
    from .scenario import Scenario


class StageManager(ScenarioComponent, Generic[TScenarioStage], ABC):
    generator: TextGenerator

    stages: List[TScenarioStage] = []
    _current_stage_idx: int
    _completed_all_stages: bool
    _auto_advance_stage: bool

    @property
    def current_stage(self) -> TScenarioStage:
        return self.stages[self._current_stage_idx]

    @property
    def completed_all_stages(self) -> bool:
        return self._completed_all_stages

    @property
    @abstractmethod
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        pass

    def __init__(
            self,
            scenario: 'Scenario',
            auto_advance_stage: bool = True,
    ) -> None:
        super().__init__(scenario)

        self.stages = []
        self._current_stage_idx = 0
        self._completed_all_stages = False

        self.generator = TextGenerator(process_id=self.instance_uid)
        self.generator.generation_params.temperature = 0
        # self.generator.generation_params.response_format = 'json_object'

        self._auto_advance_stage = auto_advance_stage
        self.loggers.stage.debug(f"StageManager initialized with auto_advance_stage={auto_advance_stage} and stage_first_speaker_mode={self.stage_first_speaker_mode} for scenario {self.template_uid}")

    async def awake(self):
        self.stages = await self.generate_stages_async()

    async def start(self):
        # For the first speaker of the first stage we defer to the ConversationController
        initial_stage_first_speaker = self.scenario.conversation_controller.first_speaker
        self.loggers.stage.debug(f"StageManager starting with initial_stage_first_speaker={initial_stage_first_speaker}")

        self.current_stage.initialize(initial_stage_first_speaker, 0)
        self.loggers.stage.debug(f"StageManager initialized first stage: {self.current_stage}")

        await self.try_send_progress_async()

    def cleanup(self):
        # del self._stages
        super().cleanup()

    async def generate_stages_async(self) -> List[TScenarioStage]:
        if (debug_stages := quiply_debug.get_stages(self.template_uid)) is not None:
            stages = debug_stages
        else:
            stages = await self._generate_stages_async()

        if stages is None or len(stages) == 0:
            stages = [ScenarioStage(
                name='Default Stage',
                description='Default Stage',
                agent_ids=[agent.template.uid for agent in self.scenario.agents]
            )]

        stages_str = f"Generated {len(stages)} stages:\n\t" + ('\n\t'.join([f"{i + 1}. {str(stage)}" for i, stage in enumerate(stages)]))
        self.loggers.stage.info(stages_str)
        return stages

    @abstractmethod
    async def _generate_stages_async(self) -> List[TScenarioStage]:
        pass

    async def step(self, message: Message):
        try:
            self.current_stage.step(message)
        except Exception as e:
            self.loggers.stage.exception(e)
            raise e

        if await self.try_advance_stage_async():
            self.scenario.exit_step = True
        if message.is_from(MessageRole.ai):
            await self.try_assess_scenario_async()

        await self.try_send_progress_async()

        # await self.try_complete_scenario_async()
        # self.scenario.defer(self.try_send_progress_async)

    def check_completed_all_stages(self):
        if self._current_stage_idx >= len(self.stages) - 1:
            self._completed_all_stages = True
            self.loggers.stage.info(f'Completed all stages')
            return True

    async def try_advance_stage_async(self) -> bool:
        advance_stage = await self.check_advance_stage_async()
        if advance_stage:
            if self.check_completed_all_stages():
                self.send_scenario_complete_notification()
                return True
            if self._auto_advance_stage:
                await self.advance_stage_async()
            else:
                self.send_stage_complete_notification()  # This will trigger a request to the user to advance the stage
        return advance_stage

    @abstractmethod
    async def check_advance_stage_async(self) -> bool:
        pass

    async def advance_stage_async(self) -> bool:
        if self.check_completed_all_stages():
            self.send_scenario_complete_notification()
            return False

        prev_stage = self.stages[self._current_stage_idx]
        self._current_stage_idx += 1

        self.loggers.stage.info(f'Advanced to stage {self._current_stage_idx + 1} of {len(self.stages)}')

        new_first_speaker, new_speaker_index = self._get_next_stage_speaker_mode(prev_stage)
        self.current_stage.initialize(new_first_speaker, new_speaker_index)

        self.send_stage_complete_announcement()

        await self.scenario.event_manager.emit(ScenarioEvent.ON_STAGE_CHANGE, self.current_stage)
        return True

    def send_stage_complete_announcement(self):
        content = f'Begin {self.current_stage.parseable_data.name}'
        pass
        # self.websocket_connection.create_message_task(MessageWsEvents.FULL_MESSAGE, EventMessage.from_announcement(content))

    def send_stage_complete_notification(self):
        pass
        # self.websocket_connection.create_scenario_task(ScenarioWsEvents.NOTIFICATION, ScenarioNotification.STAGE_COMPLETE())

    def send_scenario_complete_notification(self):
        pass
        # self.websocket_connection.create_scenario_task(ScenarioWsEvents.NOTIFICATION, ScenarioNotification.SCENARIO_COMPLETE())

    def _get_next_stage_speaker_mode(self, prev_stage: TScenarioStage) -> {Literal['user', 'ai'], int}:
        def get_next_index(idx: int) -> int:
            if idx >= len(self.scenario.agents) - 1:
                return 0
            return idx + 1

        new_index = prev_stage.first_speaker_agent_index

        if self.stage_first_speaker_mode == StageFirstSpeakerMode.USER_ALWAYS_FIRST:
            new_mode = 'user'
        elif self.stage_first_speaker_mode == StageFirstSpeakerMode.AI_ALWAYS_FIRST:
            new_mode = 'ai'
            new_index = get_next_index(prev_stage.first_speaker_agent_index)
        elif self.stage_first_speaker_mode == StageFirstSpeakerMode.ALTERNATING:
            new_mode = 'user' if prev_stage.first_speaker_type == 'ai' else 'ai'
            if new_mode == 'ai':
                new_index = get_next_index(prev_stage.first_speaker_agent_index)
        elif self.stage_first_speaker_mode == StageFirstSpeakerMode.RANDOM:
            new_mode = 'user' if random.randint(0, 1) == 0 else 'ai'
            if new_mode == 'ai':
                new_index = get_next_index(prev_stage.first_speaker_agent_index)
        else:
            raise ValueError(f"Invalid stage speaker mode: {self.stage_first_speaker_mode}")

        return new_mode, new_index

    async def try_assess_scenario_async(self) -> bool:
        assessment = await self.assess_scenario_async(self.scenario.conversation_controller.current_conversation)
        if assessment is not None:
            if assessment.complete:
                self.send_scenario_complete_notification()
            else:
                pass
                # self.websocket_connection.create_scenario_task(ScenarioWsEvents.ASSESSMENT, data=assessment)
            return True
        return False

    async def assess_scenario_async(self, conversation: Conversation) -> Optional[ScenarioAssessment]:
        prompt = prompts.scenario_assessment
        _input = prompt.format(
            stages=self.get_stages_str(),
            scenario_description=self.scenario.scenario_description,
            conversation_history=conversation.to_string(),
            format_instructions=ScenarioAssessment.get_format_instructions()
        )
        response = await self.generator.run_async(_input)
        self.loggers.stage.warning(f"assess_scenario_async response: {response}")

        try:
            return ScenarioAssessment().parse(response.content)
        except Exception as e:
            self.loggers.stage.error(f"Error parsing response: {e}")
            return None

    async def try_send_progress_async(self) -> bool:
        progress = self._get_stage_progress(self.current_stage)
        if progress is not None:
            # self.websocket_connection.create_scenario_task(ScenarioWsEvents.PROGRESS, data=progress)
            return True
        return False

    def _get_stage_progress(self, stage: TScenarioStage) -> Optional[str]:
        if stage.message_limit is None or stage.message_limit == 0:
            return "∞"
        return f"{stage.user_message_count}/{stage.message_limit}"

    @staticmethod
    def remove_before_brace(s: str) -> str:
        index = s.find('{')
        return s[index:] if index != -1 else s

    def get_stages_str(self) -> str:
        return ScenarioStage.join_string(self.stages)