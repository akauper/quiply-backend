from typing import TYPE_CHECKING

from src.framework import prompts
from src.scenario.base import AgentBuilder
from src.utils import list_to_comma_delimited_str
from src.scenario.agents.scenario_agent import ScenarioAgent

if TYPE_CHECKING:
    from .scenario import PersonalScenario


class PersonalAgentBuilder(AgentBuilder):

    def format_topic(self) -> str:
        if self.settings.topic:
            return f" about {self.settings.topic}"
        else:
            return ""

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        other_participant_names = [name for name in self.scenario.participant_names if name != agent.name]
        other_participant_names_str = list_to_comma_delimited_str(other_participant_names)

        prompt = prompts.personal.character.instructions
        return prompt.format(
            character_name=agent.name,
            topic=self.format_topic(),
            other_character_names=other_participant_names_str
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.personal.character.role_and_behaviour
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
        )

    def get_advisor_scenario_description(self) -> str:
        return f"a conversation{self.format_topic()}"
