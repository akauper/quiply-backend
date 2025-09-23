from src.models import ScenarioSpecificAnalysis
from src.scenario.models import ScenarioStage, ScenarioStageData


class PersonalStageData(ScenarioStageData):
    pass


class PersonalStage(ScenarioStage[PersonalStageData]):
    pass


class PersonalSkillsAnalysis(ScenarioSpecificAnalysis):
    pass

