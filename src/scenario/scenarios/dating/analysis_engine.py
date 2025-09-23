from typing import Type

from src.framework import prompts
from src.scenario.base import AnalysisEngine
from .models import DatingSkillsAnalysis


class DatingAnalysisEngine(AnalysisEngine[DatingSkillsAnalysis]):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[DatingSkillsAnalysis]:
        return DatingSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.dating.analysis.skills_analysis
        return prompt.format(users_name=self.users_name)
