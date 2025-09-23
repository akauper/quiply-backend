from enum import Enum

from pydantic import Field

from src.models import Metric, ScenarioSpecificAnalysis
from src.scenario.models import ScenarioStage, ScenarioStageData


class DatingStageData(ScenarioStageData):
    pass


class DatingStage(ScenarioStage[DatingStageData]):
    pass


class DatingSkillsAnalysis(ScenarioSpecificAnalysis):
    personal_presentation: Metric = Field(default_factory=Metric, description="How well the participant presents themselves in terms of appearance, confidence, and charisma. This includes their grooming, attire, and overall confidence in expressing their personality.")
    conversation_flow: Metric = Field(default_factory=Metric, description="Ability to maintain a smooth and natural conversation flow.")
    opening_line: Metric = Field(default_factory=Metric, description="Ability to start the conversation with an engaging opening line.")

    # scenario_template_id: str = 'speed_dating'
    # opening_line: Metric = Field(default_factory=Metric, description="The participant's ability to start the conversation with an engaging opening line.")
    # active_listening: Metric = Field(default_factory=Metric, description="The participant's ability to listen actively and show they are paying attention.")
    # sharing_personal_insights: Metric = Field(default_factory=Metric, description="The participant's capability to share personal information at a level appropriate for speed dating.")
    # asking_questions: Metric = Field(default_factory=Metric, description="The participant's skill in asking questions that show interest in the other person.")
    # balancing_conversation: Metric = Field(default_factory=Metric, description="The participant's ability to balance the conversation between talking about themselves and learning about the other person.")
    # conversation_flow: Metric = Field(default_factory=Metric, description="The participant's ability to maintain a smooth and natural conversation flow.")
    # closing_remarks: Metric = Field(default_factory=Metric, description="The participant's skill in ending the conversation on a positive note and expressing interest in future interaction.")
    # time_management: Metric = Field(default_factory=Metric, description="The participant's ability to manage the limited time effectively without rushing or leaving too much silence.")
    # chemistry_indicators: Metric = Field(default_factory=Metric, description="Observations of any indications of chemistry or connection between the participant and their speed dating partner.")
