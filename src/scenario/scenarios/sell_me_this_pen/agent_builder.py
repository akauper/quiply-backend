from src.framework import prompts
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.agent_builder import AgentBuilder


class SellMeThisPenAgentBuilder(AgentBuilder):

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.sell_me_this_pen.character.instructions
        return prompt.format(
            character_name=agent.name,
            users_name=self.scenario.users_name,
            selling=self.scenario.params.selling,
            audience=self.scenario.params.audience,
            location=self.scenario.params.location
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.sell_me_this_pen.character.role_and_behaviour
        return prompt.format(
            users_name=self.scenario.users_name,
            selling=self.scenario.params.selling,
            audience=self.scenario.params.audience,
            location=self.scenario.params.location,
        )

    def get_scenario_specific_personality_traits(self, agent: ScenarioAgent) -> str:
        prompt = prompts.sell_me_this_pen.character.scenario_specific_personality_traits
        return prompt.format(
            selling=self.scenario.params.selling,
            audience=self.scenario.params.audience,
            location=self.scenario.params.location,
        )

    def get_advisor_scenario_description(self) -> str:
        return f"a sales pitch selling {self.scenario.params.selling}"
    