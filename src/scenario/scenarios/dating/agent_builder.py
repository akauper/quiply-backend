import random

from src.framework import prompts
from src.scenario.base import AgentBuilder
from src.scenario.agents import ScenarioAgent


class DatingAgentBuilder(AgentBuilder):
    async def awake(self):
        await super().awake()
        random.shuffle(self.scenario.agents)

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.dating.character.instructions
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
            date_type=self.scenario.params.date_type,
            date_location=self.scenario.params.date_location,
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.dating.character.role_and_behaviour
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
        )

    def get_advisor_scenario_description(self) -> str:
        return f"a date"

    def get_scenario_specific_personality_traits(self, agent: ScenarioAgent) -> str:
        return ''
        return prompts.dating.character.personality_traits.format(
            character_name=agent.name
        )
