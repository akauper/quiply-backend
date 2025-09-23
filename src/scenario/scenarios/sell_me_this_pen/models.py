from pydantic import Field

from src.models import ScenarioSpecificAnalysis, Metric
from src.scenario.models import ScenarioStageData, ScenarioStage


class SellMeThisPenSkillsAnalysis(ScenarioSpecificAnalysis):
    professionalism: Metric = Field(description="Ability to answer questions in a professional manner.")


class SellMeThisPenStageData(ScenarioStageData):
    pass


class SellMeThisPenStage(ScenarioStage[SellMeThisPenStageData]):
    pass
