from enum import Enum
from typing import Union, Optional, List, TYPE_CHECKING

from pydantic import Field

from src.models import UIDObject
from src.scenario.models.stage import ScenarioAssessment, AgentImpression, ScenarioProgress


class ScenarioWsEvents(str, Enum):
    IMPRESSION = 'impression'
    PROGRESS = 'progress'
    ASSESSMENT = 'assessment'
    NOTIFICATION = 'notification'
    ADVISOR_COMMENT = 'advisor_comment'
    USER_ADVANCE_STAGE = 'user_advance_stage'
    USER_COMPLETE_SCENARIO = 'user_complete_scenario'


class ScenarioNotificationTypes(str, Enum):
    SCENARIO_COMPLETE = 'scenario_complete'
    STAGE_COMPLETE = 'stage_complete'
    AWAIT_USER_MESSAGE = 'await_user_message'
    SCENARIO_TERMINATED = 'scenario_terminated'
    CONNECTION_ERROR = 'connection_error'


class ScenarioNotification(UIDObject):
    type: ScenarioNotificationTypes
    message: Optional[str] = Field(default=None)
    lock_input: bool = Field(default=False)
    has_duration: bool = Field(default=False)
    custom_duration: Optional[float] = Field(default=None)

    @classmethod
    def SCENARIO_COMPLETE(cls, message: str = None, lock_input: bool = False) -> 'ScenarioNotification':
        return cls(type=ScenarioNotificationTypes.SCENARIO_COMPLETE, message=message, lock_input=lock_input)

    @classmethod
    def STAGE_COMPLETE(cls, message: str = None, lock_input: bool = False) -> 'ScenarioNotification':
        return cls(type=ScenarioNotificationTypes.STAGE_COMPLETE, message=message, lock_input=lock_input)

    @classmethod
    def AWAIT_USER_MESSAGE(cls, message: str = None) -> 'ScenarioNotification':
        return cls(type=ScenarioNotificationTypes.AWAIT_USER_MESSAGE, message=message, lock_input=False)

    @classmethod
    def SCENARIO_TERMINATED(cls, message: str = None) -> 'ScenarioNotification':
        return cls(type=ScenarioNotificationTypes.SCENARIO_TERMINATED, message=message, lock_input=True)

    @classmethod
    def CONNECTION_ERROR(cls, message: str = None) -> 'ScenarioNotification':
        return cls(type=ScenarioNotificationTypes.CONNECTION_ERROR, message=message, lock_input=True)


# ScenarioWsDataTypes = Union[ScenarioNotification, ScenarioCompleteState, Progress, AgentImpression, List[AgentImpression], str, None]
ScenarioWsDataTypes = Union[ScenarioNotification, ScenarioAssessment, ScenarioProgress, AgentImpression, List[AgentImpression], str, None]
