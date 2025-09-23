from abc import ABC, abstractmethod
from types import TracebackType
from typing import List, Type, Optional, TypeVar

from src.async_object import AsyncObject
from src.exceptions import BaseScenarioException
from src.models import (
    ScenarioInstance,
    ScenarioSchema,
    ScenarioConfig,
    AccountData,
)
from src.services import storage_service
from src.utils import logger, is_empty_string

# from src.websocket import ScenarioWsEvents, ScenarioNotification, WebSocketConnection
from src.websocket import WebSocketConnection
from .agent_builder import AgentBuilder
from .analysis_engine import AnalysisEngine
from .component import ScenarioComponent
from .component_manager import ComponentManager
from .conversation_controller import ConversationController
from .event_manager import EventManager
from .lifecycle_manager import LifecycleManager
from .scenario_state_base import ScenarioStateObject
from .stage_manager import StageManager
from .voice_streaming import ScenarioVoiceStreaming
from ..agents.scenario_agent import ScenarioAgent
from ..models.base_scenario_params import BaseScenarioParams
from ..util import ScenarioLoggers, GenericScenarioLogger
from ...settings import ScenarioSettings, quiply_settings

TScenarioParams = TypeVar("TScenarioParams", bound=BaseScenarioParams)
TScenarioComponent = TypeVar("TScenarioComponent", bound=ScenarioComponent)
TConversationController = TypeVar(
    "TConversationController", bound=ConversationController
)
TStageManager = TypeVar("TStageManager", bound=StageManager)
TAgentBuilder = TypeVar("TAgentBuilder", bound=AgentBuilder)
TAnalysisEngine = TypeVar("TAnalysisEngine", bound=AnalysisEngine)


class Scenario(ScenarioStateObject, AsyncObject, ABC):
    """
    The Scenario class is the main class that manages the scenario state and the components of the scenario.
    It handles the lifecycle of a scenario, including starting, updating, and ending the scenario.
    """

    # region Fields
    logger: GenericScenarioLogger
    loggers: ScenarioLoggers
    settings: ScenarioSettings

    instance: ScenarioInstance
    template: ScenarioSchema
    params: TScenarioParams

    event_manager: EventManager
    component_manager: ComponentManager
    lifecycle_manager: LifecycleManager
    voice_streaming: ScenarioVoiceStreaming

    agents: List[ScenarioAgent]
    special_agents: List[ScenarioAgent]
    mentor: ScenarioAgent

    scenario_description: str

    # endregion

    # region Properties
    @property
    def frame_rate(self) -> float:
        return 99999

    @property
    def template_uid(self) -> str:
        return self.template.uid

    @property
    def instance_uid(self) -> str:
        return self.instance.uid

    @property
    def scenario_config(self) -> ScenarioConfig:
        return self.instance.scenario_config

    @property
    def account_data(self) -> AccountData:
        return self.instance.account_data

    @property
    def scenario_name(self) -> str:
        return self.template.name

    @property
    def user_uid(self) -> str:
        return self.instance.user_id

    @property
    def users_name(self) -> str:
        return self.instance.account_data.first_name

    @property
    def users_prefix(self) -> str:
        return f"{self.users_name}: "

    @property
    def participant_names(self) -> List[str]:
        """Returns a list of all the names of the participants in the scenario. (All agent names + users name)"""
        return [agent.name for agent in self.agents] + [self.users_name]

    @property
    def websocket_connection(self) -> WebSocketConnection:
        return self.lifecycle_manager.websocket_connection

    @property
    def conversation_controller(self) -> TConversationController:
        return self.component_manager.conversation_controller

    @property
    def stage_manager(self) -> TStageManager:
        return self.component_manager.stage_manager

    @property
    def agent_builder(self) -> TAgentBuilder:
        return self.component_manager.agent_builder

    @property
    def analysis_engine(self) -> TAnalysisEngine:
        return self.component_manager.analysis_engine

    # endregion

    # region Constructor
    def __init__(
        self,
        scenario_instance: ScenarioInstance,
        settings: ScenarioSettings = None,
    ) -> None:
        super().__init__()

        try:
            if settings:
                self.settings = settings
            else:
                self.settings = quiply_settings.scenario

            self.logger = GenericScenarioLogger(self.settings.logging)
            self.loggers = ScenarioLoggers(self.settings.logging)

            self.instance = scenario_instance
            self.template = storage_service.get_scenario_schema(
                scenario_instance.schema_id
            )
            # self.params = BaseScenarioParams(
            #     duration=self.scenario_config.duration,
            #     difficulty=self.scenario_config.difficulty,
            # )
            # self._init_params()

            self.params = self._get_params()
            self.params.actor_ids = self.scenario_config.actor_ids

            self.agents = []
            self.special_agents = []

            self.event_manager = EventManager()
            self.component_manager = ComponentManager(
                self,
                conversation_controller=self.create_conversation_controller(),
                stage_manager=self.create_stage_manager(),
                agent_builder=self.create_agent_builder(),
                analysis_engine=self.create_analysis_engine(),
            )
            self.lifecycle_manager = LifecycleManager(self, self.component_manager)

            self.scenario_description = self._format_scenario_description()
        except Exception as e:
            raise e

    @abstractmethod
    def _get_params(self) -> TScenarioParams:
        pass

    def cleanup(self) -> None:
        if self.component_manager:
            self.component_manager.cleanup()
        if self.lifecycle_manager:
            self.lifecycle_manager.cleanup()

        super().cleanup()

    # endregion

    def get_additional_scenario_information(self) -> str:
        additional_information = self.scenario_config.scenario_additional_information
        if additional_information is not None and not is_empty_string(
            additional_information
        ):
            logger.warning("Got additional information")
            logger.warning(additional_information)
            additional_information = f"The following is IMPORTANT additional information about the {self.scenario_name.lower()}: {additional_information}"
        return additional_information if additional_information is not None else ""

    # region Abstract methods
    @abstractmethod
    def get_initializing_message(self) -> str:
        pass

    @abstractmethod
    def _format_scenario_description(self) -> str:
        pass

    @abstractmethod
    def create_conversation_controller(self) -> TConversationController:
        """Factory method to create the appropriate conversation controller. Should be implemented by subclasses."""

    @abstractmethod
    def create_agent_builder(self) -> TAgentBuilder:
        """Factory method to create the appropriate agent builder. Should be implemented by subclasses."""

    @abstractmethod
    def create_analysis_engine(self) -> TAnalysisEngine:
        """Factory method to create the appropriate analysis engine. Should be implemented by subclasses."""

    @abstractmethod
    def create_stage_manager(self) -> TStageManager:
        """Factory method to create the appropriate stage manager. Should be implemented by subclasses."""

    # endregion

    def handle_exception(
        self,
        exc_type: Optional[Type[BaseScenarioException]],
        exc_val: Optional[BaseScenarioException],
        exc_tb: Optional[TracebackType],
    ):
        if exc_type is not None:
            logger.exception(
                f"An exception of type {exc_type} occurred with value {exc_val} and traceback {exc_tb}"
            )
            # self.websocket_connection.create_scenario_task(
            #     ScenarioWsEvents.NOTIFICATION,
            #     ScenarioNotification.CONNECTION_ERROR("fff"),
            # )
            # raise exc_val
