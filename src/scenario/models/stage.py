import time
from enum import Enum
from typing import Optional, List, Generic, TypeVar, Literal

from pydantic import Field, BaseModel

from src.framework import Message, MessageRole
from src.models import ParseableModel


class ScenarioCompleteState(ParseableModel):
    complete: bool = Field(default=False, description="Indicates whether the conversation has logically concluded based on the given message(s)")
    confidence: float = Field(default=0.0, description="A floating-point value between 0.0 and 1.0, reflecting your level of certainty regarding the conclusion status")
    reasoning: str = Field(default="", description="A brief textual explanation providing the basis for your judgment on whether the conversation has concluded or not")


class ScenarioProgress(ParseableModel):
    progress: float = Field(default=0.0, description="A floating-point value between 0 and 1 that quantifies the completion level of the scenario.")
    reasoning: str = Field(default='', description="A concise textual explanation to justify your progress.")


class ScenarioAssessment(ParseableModel):
    complete: bool = Field(default=False, description="Indicates whether the conversation has logically concluded based on the given message(s)")
    progress: float = Field(default=0.0, description="A floating-point value between 0 and 1 that quantifies the completion level of the scenario.")
    reasoning: str = Field(default='', description="A concise textual explanation to justify your assessment.")
    confidence: float = Field(default=0.0, description="A floating-point value between 0.0 and 1.0, reflecting your level of certainty regarding the conclusion status")


class AgentImpression(ParseableModel):
    character_name: str
    impression: float = Field(default=0.0, description="A floating-point value between 0 and 1, indicating your impression of the user.")
    reasoning: str = Field(default='', description="A concise textual explanation to justify your impression score.")


class StageFirstSpeakerMode(str, Enum):
    USER_ALWAYS_FIRST = 'user'
    AI_ALWAYS_FIRST = 'ai'
    ALTERNATING = 'alternating'
    RANDOM = 'random'


class ScenarioStageData(ParseableModel):
    name: str = Field(description="The name of the stage", examples=["Introduction", "Conclusion", "Background"])
    description: str = Field(description="The description of the stage", examples=["Getting to know the candidate", "Wrapping up the date", "Learning about the users background"])


TScenarioStageData = TypeVar("TScenarioStageData", bound=ScenarioStageData)


class ScenarioStage(BaseModel, Generic[TScenarioStageData]):
    parseable_data: TScenarioStageData
    """ The data that is used to parse the stage """

    agent_ids: List[str] = Field(default_factory=list)
    """ A list of character ids that are involved in the stage """

    first_speaker_type: Literal['user', 'ai'] = Field(default='user')
    """ The type of speaker for the stage """

    first_speaker_agent_index: int = Field(default=0)
    """ The index of the speaker for the stage """

    message_limit: int = Field(default=0)
    """ The maximum number of messages allowed in the stage """

    user_messages: List[Message] = Field(default_factory=list)
    """ A list of messages sent by the user """

    agent_messages: List[Message] = Field(default_factory=list)
    """ A list of messages sent by the agent"""

    sent_advisor_message_count_warning: bool = Field(default=False)
    """ Indicates whether the advisor has sent a message warning that the user has two messages left """

    time_limit: float = Field(default=0.0)
    """ The maximum amount of time allowed in the stage """

    start_time: float = Field(default=0.0)
    """ The time the stage started """

    end_time: float = Field(default=0.0)
    """ The time the stage will end """

    send_advisor_time_warning: bool = Field(default=False)
    """ Indicates whether the advisor has sent a one minute warning message """

    @property
    def name(self) -> str:
        return self.parseable_data.name

    @property
    def description(self) -> str:
        return self.parseable_data.description

    @property
    def user_message_count(self) -> int:
        return len(self.user_messages)

    @property
    def agent_message_count(self) -> int:
        return len(self.agent_messages)

    @property
    def total_message_count(self) -> int:
        return self.user_message_count + self.agent_message_count

    @property
    def is_over_message_limit(self) -> bool:
        """Returns True if the number of messages sent by the user or agent is >= than the message limit
        and the total number of messages is even"""
        if self.message_limit == 0:
            return False
        most = max(self.user_message_count, self.agent_message_count)
        return most >= self.message_limit and self.total_message_count % 2 == 0

    @property
    def message_progress(self) -> Optional[float]:
        if self.message_limit == 0:
            return None
        most_messages = max(len(self.user_messages), len(self.agent_messages))
        return most_messages / self.message_limit

    @property
    def is_past_time(self):
        return self.end_time != 0 and time.time() > self.end_time

    @property
    def time_remaining(self):
        if self.end_time == 0:
            return 0
        return self.end_time - time.time()

    @property
    def time_progress(self) -> Optional[float]:
        if self.end_time == 0:
            return None
        return 1 - (self.time_remaining / self.time_limit)

    @property
    def is_over_limit(self) -> bool:
        return self.is_over_message_limit or self.is_past_time

    def initialize(self, first_speaker_type: Literal['user', 'ai'], first_speaker_agent_index: int):
        self.first_speaker_type = first_speaker_type
        self.first_speaker_agent_index = first_speaker_agent_index

        self.start_time = time.time()
        if self.time_limit != 0:
            self.end_time = self.start_time + self.time_limit

    def step(self, message: Message):
        if message.is_from(MessageRole.user):
            self.user_messages.append(message)
        elif message.is_from(MessageRole.ai):
            self.agent_messages.append(message)

    def format_string(self):
        return f"{self.name}: {self.description}"

    @classmethod
    def join_string(cls, stages: List['ScenarioStage']):
        return "\n".join([f"{i + 1}. {stage.format_string()}" for i, stage in enumerate(stages)])


TScenarioStage = TypeVar("TScenarioStage", bound=ScenarioStage)
