from typing import Type

from src.framework import prompts
from src.scenario import AnalysisEngine
from .models import ConversationSkillsAnalysis


class ConversationAnalysisEngine(AnalysisEngine):

    @classmethod
    def get_scenario_specific_cls(cls) -> Type[ConversationSkillsAnalysis]:
        return ConversationSkillsAnalysis

    def format_skills_general(self) -> str:
        prompt = prompts.conversation.analysis.skills_analysis
        return prompt.format(users_name=self.users_name)
