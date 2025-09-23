from typing import Type

from src.framework import prompts
from src.scenario import AnalysisEngine
from .models import ElevatorPitchSkillsAnalysis


class ElevatorPitchAnalysisEngine(AnalysisEngine[ElevatorPitchSkillsAnalysis]):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[ElevatorPitchSkillsAnalysis]:
        return ElevatorPitchSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.elevator_pitch.analysis.skills_analysis
        return prompt.format(
            users_name=self.scenario.users_name
        )