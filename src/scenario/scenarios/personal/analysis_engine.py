from typing import Type

from src.framework import prompts
from src.scenario import AnalysisEngine
from .models import PersonalSkillsAnalysis


class PersonalAnalysisEngine(AnalysisEngine):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[PersonalSkillsAnalysis]:
        return PersonalSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.personal.analysis.skills_analysis
        return prompt.format(users_name=self.users_name)
