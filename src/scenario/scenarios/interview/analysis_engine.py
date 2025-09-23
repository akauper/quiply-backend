from typing import Type

from src.framework import prompts
from .models import InterviewSkillsAnalysis
from src.scenario.base import AnalysisEngine


class InterviewAnalysisEngine(AnalysisEngine[InterviewSkillsAnalysis]):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[InterviewSkillsAnalysis]:
        return InterviewSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.interview.analysis.skills_analysis
        return prompt.format(
            company_name=self.scenario.company_name,
            job_title=self.scenario.job_title,
            users_name=self.users_name,
        )
