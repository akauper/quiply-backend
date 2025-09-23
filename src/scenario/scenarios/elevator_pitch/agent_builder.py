from src.framework import prompts
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.agent_builder import AgentBuilder


class ElevatorPitchAgentBuilder(AgentBuilder):

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.elevator_pitch.character.instructions
        return prompt.format(
            character_name=agent.name,
            users_name=self.scenario.users_name,
            audience_type=self.settings.audience_type
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.elevator_pitch.character.role_and_behaviour
        return prompt.format(
            character_name=agent.name,
            audience_type=self.settings.audience_type,
            users_name=self.scenario.users_name
        )

    def get_advisor_scenario_description(self) -> str:
        return f"an elevator pitch titled {self.scenario.pitch_title}"
    