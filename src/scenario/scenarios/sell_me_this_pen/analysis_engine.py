from typing import Type

from src.framework import prompts
from src.scenario import AnalysisEngine
from .models import SellMeThisPenSkillsAnalysis


class SellMeThisPenAnalysisEngine(AnalysisEngine[SellMeThisPenSkillsAnalysis]):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[SellMeThisPenSkillsAnalysis]:
        return SellMeThisPenSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.sell_me_this_pen.analysis.skills_analysis
        return prompt.format(
            users_name=self.scenario.users_name,
            selling=self.scenario.params.selling,
        )