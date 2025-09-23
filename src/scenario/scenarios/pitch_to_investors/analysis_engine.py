from typing import Type

from src.framework import prompts
from src.scenario import AnalysisEngine
from .models import PitchToInvestorsSkillsAnalysis


class PitchToInvestorsAnalysisEngine(AnalysisEngine[PitchToInvestorsSkillsAnalysis]):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[PitchToInvestorsSkillsAnalysis]:
        return PitchToInvestorsSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.pitch_to_investors.analysis.skills_analysis
        return prompt.format(
            users_name=self.scenario.users_name
        )