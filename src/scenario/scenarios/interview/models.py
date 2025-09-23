from typing import Optional, List

from pydantic import Field

from src.models import Metric, ScenarioSpecificAnalysis, ParseableModel
from src.scenario.models import ScenarioStage, ScenarioStageData


class InterviewSkillsAnalysis(ScenarioSpecificAnalysis):
    depth_of_knowledge: Metric = Field(default_factory=Metric, description="Level of knowledge and expertise in specific topics discussed during social interactions. Provide feedback on how well they understand and convey complex ideas, and how effectively they use their knowledge to contribute to meaningful discussions.")
    clarity_and_conciseness: Metric = Field(description="Ability to answer questions clearly and concisely.")
    professionalism: Metric = Field(description="Ability to answer questions in a professional manner.")


class InterviewStageData(ScenarioStageData):
    numberOfQuestions: Optional[int] = Field(default=0, description="The number of questions in the stage")


class InterviewStage(ScenarioStage[InterviewStageData]):
    def format_string(self):
        return super().format_string() + f" -- Typical number of questions: {self.parseable_data.numberOfQuestions}"


class InterviewStageDataList(ParseableModel):
    stage_datas: List[InterviewStageData] = Field(default_factory=list, description="A list of stage data in the scenario")
