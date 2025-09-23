from typing import Union

from src.framework import prompts
from src.models import ScenarioInstance
from src.scenario.base import Scenario
from src.utils import str_to_seconds, loggers
from .analysis_engine import DebateAnalysisEngine
from .agent_builder import DebateAgentBuilder
from .conversation_controller import DebateConversationController
from .stage_manager import DebateStageManager
from src.scenario.agents.scenario_agent import ScenarioAgent


class Debate(Scenario):
    @property
    def moderator(self) -> ScenarioAgent:
        return self.special_agents[0]

    def _init_params(self):
        self.params.topic = self.scenario_config.field_values['topic']

        if self.params.duration is None:
            self.params.stage_count = 3
            self.params.stage_message_limit = 5
        else:
            duration = self.params.duration.lower()
            if duration == 'short':
                self.params.stage_count = 2
                self.params.stage_message_limit = 4
            elif duration == 'medium':
                self.params.stage_count = 4
                self.params.stage_message_limit = 5
            elif duration == 'long':
                self.params.stage_count = 6
                self.params.stage_message_limit = 8
            else:
                loggers.scenario.warning(f"Invalid duration value: {duration}. Setting to default values.")
                self.params.stage_count = 3
                self.params.stage_message_limit = 5

    def _parse_difficulty_description(self, difficulty: str) -> None:
        pass

    def create_conversation_controller(self):
        return DebateConversationController(scenario=self)

    def create_agent_builder(self):
        return DebateAgentBuilder(scenario=self)

    def create_analysis_engine(self):
        return DebateAnalysisEngine(scenario=self)

    def create_stage_manager(self):
        return DebateStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The debate will begin shortly."

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"The following is IMPORTANT additional information about this debate: {context}"

        prompt = prompts.debate.description

        formatted = prompt.format(
            topic=self.params.topic,
            moderator_name=self.moderator.template.name,
            debater_names=self.participant_names,
            additional_scenario_context=additional_scenario_context,
        )
        return formatted
