from src.framework import prompts
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base import AgentBuilder


class InterviewAgentBuilder(AgentBuilder):

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        prompt = prompts.interview.character.instructions
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
            job_title=self.settings.job_title,
            company_name=self.settings.company_name
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.interview.character.role_and_behaviour
        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
        )

    async def get_extra_information_async(
            self,
            agent: ScenarioAgent,
            scenario_instructions: str,
            scenario_additional_information: str,
            role_and_behaviour: str,
            personality: str,
    ) -> str:
        stages_str = self.scenario.stage_manager.get_stages_str()
        if stages_str is None or stages_str == "":
            return ""
        prompt = prompts.interview.character.extra_information
        return prompt.format(
            interview_stages=self.scenario.stage_manager.get_stages_str()
        )

    def get_advisor_scenario_description(self) -> str:
        return f"an ongoing job interview for the position of {self.settings.job_title} at {self.settings.company_name}"
