from src.framework import prompts
from src.models import ScenarioInstance
from src.scenario.base import Scenario
from src.utils import str_to_seconds, list_to_comma_delimited_str
from .agent_builder import ConversationAgentBuilder
from .analysis_engine import ConversationAnalysisEngine
from .conversation_controller import ConversationConversationController
from .stage_manager import ConversationStageManager


class ConversationScenario(Scenario):

    def _init_params(self):
        self.params.topic = self.scenario_config.field_values['topic']

    def create_conversation_controller(self):
        return ConversationConversationController(scenario=self)

    def create_agent_builder(self):
        return ConversationAgentBuilder(scenario=self)

    def create_analysis_engine(self):
        return ConversationAnalysisEngine(scenario=self)

    def create_stage_manager(self):
        return ConversationStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The chat will begin shortly."

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"The following is IMPORTANT additional information about this chat: {context}"

        agent_names = [agent.name for agent in self.agents]
        agent_names_str = list_to_comma_delimited_str(agent_names)

        prompt = prompts.conversation.description
        formatted = prompt.format(
            topic=self.params.topic,
            character_names=agent_names_str,
            additional_scenario_context=additional_scenario_context,
        )
        return formatted
