from enum import Enum

from pydantic import Field

from src.models import ScenarioSpecificAnalysis, Metric
from src.scenario.models import ScenarioStage, ScenarioStageData


class DebateEvent(str, Enum):
    ROUND_COMPLETE = 'round_complete'
    LAST_MESSAGE = 'last_message'
    MODERATOR_MESSAGE = 'moderator_message'


class DebateStageData(ScenarioStageData):
    question: str = Field(description="The question for the debate stage")


class DebateStage(ScenarioStage[DebateStageData]):
    @property
    def question(self) -> str:
        return self.parseable_data.question


class DebateSkillsAnalysis(ScenarioSpecificAnalysis):
    persuasion: Metric = Field(default_factory=Metric, description="Ability to persuade others to their point of view.")
    arguments: Metric = Field(default_factory=Metric, description="Ability to make strong arguments to support their point of view.")
    counter_arguments: Metric = Field(default_factory=Metric, description="Ability to counter arguments made by others.")

    # topic_engagement: Metric = Field(default_factory=Metric, description="The participant's engagement level with the topic of the conversation.")
    # contribution_to_discussion: Metric = Field(default_factory=Metric, description="The participant's ability to contribute meaningfully to the conversation.")
    # interpersonal_interaction: Metric = Field(default_factory=Metric, description="The participant's skill in interacting with multiple group members.")
    # active_listening: Metric = Field(default_factory=Metric, description="The participant's ability to listen to others' points of view and show understanding.")
    # respectful_disagreement: Metric = Field(default_factory=Metric, description="The participant's ability to disagree respectfully and constructively when necessary.")
    # encouraging_others: Metric = Field(default_factory=Metric, description="The participant's ability to encourage quieter members of the group to participate.")
    # adaptability: Metric = Field(default_factory=Metric, description="The participant's ability to adapt their conversational approach based on the group's dynamics and responses.")
    # conflict_resolution: Metric = Field(default_factory=Metric, description="The participant's skills in managing and resolving any conflicts that arise during the conversation.")
    # summarizing_points: Metric = Field(default_factory=Metric, description="The participant's ability to summarize or synthesize group opinions or points made during the discussion.")
    # closing_thoughts: Metric = Field(default_factory=Metric, description="The participant's skill in concluding their thoughts and the conversation about the topic.")
    #
