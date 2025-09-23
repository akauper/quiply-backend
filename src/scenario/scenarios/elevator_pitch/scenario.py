from typing import Optional

from devtools import debug

from src.framework import prompts
from src.models import ScenarioInstance
from src.scenario.base.scenario import Scenario
from src.utils import str_to_seconds, list_to_comma_delimited_str, loggers
from .analysis_engine import ElevatorPitchAnalysisEngine
from .agent_builder import ElevatorPitchAgentBuilder
from .conversation_controller import ElevatorPitchConversationController
from .stage_manager import ElevatorPitchStageManager


class ElevatorPitch(Scenario):

    def _init_params(self):
        super()._init_params()
        debug(self.scenario_config)
        self.params.audience_type = self.scenario_config.field_values.get('audience_type', None)
        self.params.audience_inclination = self.scenario_config.field_values.get('audience_inclination', None)

        if self.params.duration is None:
            self.params.stage_message_limit = 7
        else:
            duration = self.params.duration.lower()
            if duration == 'short':
                self.params.stage_message_limit = 5
            elif duration == 'medium':
                self.params.stage_message_limit = 7
            elif duration == 'long':
                self.params.stage_message_limit = 12
            else:
                loggers.scenario.warning(f"Invalid duration value: {duration}. Setting to default values.")
                self.params.stage_message_limit = 5

    def create_conversation_controller(self) -> ElevatorPitchConversationController:
        return ElevatorPitchConversationController(scenario=self)

    def create_agent_builder(self) -> ElevatorPitchAgentBuilder:
        return ElevatorPitchAgentBuilder(scenario=self)

    def create_analysis_engine(self) -> ElevatorPitchAnalysisEngine:
        return ElevatorPitchAnalysisEngine(scenario=self)

    def create_stage_manager(self) -> ElevatorPitchStageManager:
        return ElevatorPitchStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The investors will arrive soon."

    def _format_scenario_description(self) -> str:
        if len(self.agents) > 1:
            agent_name_list = [agent.name for agent in self.agents]
            audience_names = list_to_comma_delimited_str(agent_name_list)
            prompt = prompts.elevator_pitch.group_investor_description
        else:
            audience_names = self.agents[0].name
            prompt = prompts.elevator_pitch.single_investor_description

        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"""The following is IMPORTANT additional information about the elevator pitch: {context}
            This may include details like the setting of the pitch (e.g., a casual meeting, a formal investor gathering), the main objectives of the pitcher, and specific interests or concerns of the listener."""
        formatted = prompt.format(
            audience_names=audience_names,
            audience_type=self.params.audience_type,
            users_name=self.users_name,
            additional_scenario_context=additional_scenario_context
        )

        return formatted
