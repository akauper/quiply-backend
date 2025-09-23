from typing import Type

from src.framework import prompts
from src.scenario.base import AnalysisEngine
from .models import DebateSkillsAnalysis


class DebateAnalysisEngine(AnalysisEngine):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[DebateSkillsAnalysis]:
        return DebateSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.debate.analysis.skills_analysis

        return prompt.format(
            users_name=self.users_name,
            topic=self.scenario.topic,
            opponents_name=self.scenario.agents[0].name
        )
