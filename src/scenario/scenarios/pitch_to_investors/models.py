from pydantic import Field

from src.models import ScenarioSpecificAnalysis, Metric
from src.scenario.models import ScenarioStageData, ScenarioStage


class PitchToInvestorsSkillsAnalysis(ScenarioSpecificAnalysis):
    professionalism: Metric = Field(description="Ability to answer questions in a professional manner.")


class PitchToInvestorsStageData(ScenarioStageData):
    pass


class PitchToInvestorsStage(ScenarioStage[PitchToInvestorsStageData]):
    pass
