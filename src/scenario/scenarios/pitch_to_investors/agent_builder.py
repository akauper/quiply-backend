from src.framework import prompts
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.agent_builder import AgentBuilder


class PitchToInvestorsAgentBuilder(AgentBuilder):

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.pitch_to_investors.character.instructions
        return prompt.format(
            character_name=agent.name,
            users_name=self.scenario.users_name,
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.pitch_to_investors.character.role_and_behaviour
        return prompt.format(
            users_name=self.scenario.users_name
        )

    def get_scenario_specific_personality_traits(self, agent: ScenarioAgent) -> str:
        prompt = prompts.pitch_to_investors.character.scenario_specific_personality_traits
        return prompt.format(
        )

    def get_advisor_scenario_description(self) -> str:
        return f"a pitch titled {self.scenario.pitch_title}"
    