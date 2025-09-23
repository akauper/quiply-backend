from src.models import ScenarioSpecificAnalysis
from src.scenario.models import ScenarioStage, ScenarioStageData


class ConversationStageData(ScenarioStageData):
    pass


class ConversationStage(ScenarioStage[ConversationStageData]):
    pass


class ConversationSkillsAnalysis(ScenarioSpecificAnalysis):
    pass

