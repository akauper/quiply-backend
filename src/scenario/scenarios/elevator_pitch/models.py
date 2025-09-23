from pydantic import Field

from src.models import ScenarioSpecificAnalysis, Metric
from src.scenario.models import ScenarioStageData, ScenarioStage


class ElevatorPitchSkillsAnalysis(ScenarioSpecificAnalysis):
    professionalism: Metric = Field(description="Ability to answer questions in a professional manner.")


class ElevatorPitchStageData(ScenarioStageData):
    pass


class ElevatorPitchStage(ScenarioStage[ElevatorPitchStageData]):
    pass
