from src.framework import prompts
from src.scenario.base import Scenario
from src.utils import loggers
from .agent_builder import SpeedDatingAgentBuilder
from .analysis_engine import SpeedDatingAnalysisEngine
from .conversation_controller import SpeedDatingConversationController
from .stage_manager import SpeedDatingStageManager


class SpeedDating(Scenario):

    def _init_params(self):
        self.params.stage_count = len(self.scenario_config.actor_ids)

        if self.params.duration is None:
            self.params.stage_message_limit = 6
        else:
            duration = self.params.duration.lower()
            if duration == 'short':
                self.params.stage_message_limit = 6
            elif duration == 'medium':
                self.params.stage_message_limit = 8
            elif duration == 'long':
                self.params.stage_message_limit = 10
            else:
                loggers.scenario.warning(f"Invalid duration value: {duration}. Setting to default values.")
                self.params.stage_message_limit = 6

    def create_conversation_controller(self) -> SpeedDatingConversationController:
        return SpeedDatingConversationController(scenario=self)

    def create_agent_builder(self) -> SpeedDatingAgentBuilder:
        return SpeedDatingAgentBuilder(scenario=self)

    def create_analysis_engine(self) -> SpeedDatingAnalysisEngine:
        return SpeedDatingAnalysisEngine(scenario=self)

    def create_stage_manager(self) -> SpeedDatingStageManager:
        return SpeedDatingStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The dates will begin soon!"

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"The following is IMPORTANT additional information about the speed dating event: {context}"

        prompt = prompts.speed_dating.description
        formatted = prompt.format(
            additional_scenario_context=additional_scenario_context,
        )
        return formatted

