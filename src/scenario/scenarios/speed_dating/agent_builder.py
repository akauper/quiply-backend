import random

from src.framework import prompts
from src.scenario.base import AgentBuilder
from src.scenario.agents import ScenarioAgent


class SpeedDatingAgentBuilder(AgentBuilder):
    async def awake(self):
        await super().awake()
        random.shuffle(self.scenario.agents)

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.speed_dating.character.instructions
        return prompt.format(
            character_name=agent.name
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.speed_dating.character.role_and_behaviour
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
        )

    def get_advisor_scenario_description(self) -> str:
        return f"an ongoing speed dating event"
