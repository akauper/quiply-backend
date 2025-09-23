from src.framework import prompts
from src.scenario.base import Scenario
from src.utils import loggers
from .agent_builder import DatingAgentBuilder
from .analysis_engine import DatingAnalysisEngine
from .conversation_controller import DatingConversationController
from .stage_manager import DatingStageManager
from .params import DatingParams


class Dating(Scenario):

    def _get_params(self) -> DatingParams:
        try:
            field_configs = self.scenario_config.get_field_configs()
            date_type_field = field_configs.get("date_type").get("date_type")
            date_location_field = field_configs.get("date_location").get("date_location")
            return DatingParams(
                date_type=date_type_field.value,
                date_location=date_location_field.value,
            )
        except Exception as e:
            loggers.scenario.error(f"Failed to get dating params: {e}")
            raise e

    def create_conversation_controller(self) -> DatingConversationController:
        return DatingConversationController(scenario=self)

    def create_agent_builder(self) -> DatingAgentBuilder:
        return DatingAgentBuilder(scenario=self)

    def create_analysis_engine(self) -> DatingAnalysisEngine:
        return DatingAnalysisEngine(scenario=self)

    def create_stage_manager(self) -> DatingStageManager:
        return DatingStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The dates will begin soon!"

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"The following is IMPORTANT additional information about the date: {context}"

        prompt = prompts.dating.description
        formatted = prompt.format(
            additional_scenario_context=additional_scenario_context,
        )
        return formatted

