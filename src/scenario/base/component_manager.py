import asyncio
from typing import TypeVar, List, Type, Optional, TYPE_CHECKING

from devtools import debug

from src.framework import Message
from src.utils import loggers
from .agent_builder import AgentBuilder
from .analysis_engine import AnalysisEngine
from .component import ScenarioComponent
from .conversation_controller import ConversationController
from .stage_manager import StageManager
from ...exceptions import ScenarioStepException

if TYPE_CHECKING:
    from .scenario import Scenario

TScenarioComponent = TypeVar("TScenarioComponent", bound=ScenarioComponent)


class ComponentManager:

    scenario: 'Scenario'
    _break_step: bool

    _components: List[TScenarioComponent]

    conversation_controller: ConversationController
    stage_manager: StageManager
    agent_builder: AgentBuilder
    analysis_engine: AnalysisEngine

    current_frame: int

    def __init__(
            self,
            scenario: 'Scenario',
            *,
            conversation_controller: ConversationController,
            stage_manager: StageManager,
            agent_builder: AgentBuilder,
            analysis_engine: AnalysisEngine,
    ):
        self.scenario = scenario
        self._break_step = False

        self.conversation_controller = conversation_controller
        self.stage_manager = stage_manager
        self.agent_builder = agent_builder
        self.analysis_engine = analysis_engine

        self._components = [
            conversation_controller,
            stage_manager,
            agent_builder,
            analysis_engine,
        ]

        self.current_frame = 0

        self._reorder_components()

    def cleanup(self):
        for component in self._components:
            component.cleanup()

        del self._components

    def _reorder_components(self) -> None:
        self._components.sort(key=lambda component: component.priority)

    def add_component(self, component: TScenarioComponent) -> TScenarioComponent:
        self._components.append(component)
        self._reorder_components()
        return component

    def get_component(self, component_type: Type[TScenarioComponent]) -> Optional[TScenarioComponent]:
        for component in self._components:
            if isinstance(component, component_type):
                return component
        return None

    async def awake(self):
        for component in self._components:
            await component.awake()

    async def start(self):
        for component in self._components:
            await component.start()

    async def step(self, message: Message, mentor_step: bool) -> None:
        if not message:
            loggers.framework.warning("Step called without a message")
            return
        try:
            self._break_step = False

            for component in self._components:
                if mentor_step:
                    await component.step_mentor(message)
                else:
                    await component.step(message)
        except Exception as e:
            self.scenario.handle_exception(ScenarioStepException, ScenarioStepException(e.args), e.__traceback__)

        await self._late_step(message, mentor_step)

    async def _late_step(self, message: Message, mentor_step: bool) -> None:
        try:
            for component in self._components:
                if mentor_step:
                    await component.late_step_mentor(message)
                else:
                    await component.late_step(message)
        except Exception as e:
            self.scenario.handle_exception(ScenarioStepException, ScenarioStepException(e.args), e.__traceback__)

    async def update(self) -> None:
        cur_time = 0
        sleep_time = 0.25
        while cur_time < self.scenario.frame_rate:
            await asyncio.sleep(sleep_time)
            cur_time += sleep_time

        self.current_frame += 1

        try:
            for component in self._components:
                await component.update(self.current_frame)
        except Exception as e:
            self.scenario.handle_exception(ScenarioStepException, ScenarioStepException(e.args), e.__traceback__)
