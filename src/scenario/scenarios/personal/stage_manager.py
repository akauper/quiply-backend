from typing import List, TYPE_CHECKING, Optional

from src.framework import Conversation
from src.scenario.base import StageManager
from src.scenario.models import StageFirstSpeakerMode, ScenarioAssessment, TScenarioStage
from .models import PersonalStage, PersonalStageData

if TYPE_CHECKING:
    from .scenario import PersonalScenario


class PersonalStageManager(StageManager[PersonalStage]):

    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.USER_ALWAYS_FIRST

    async def check_advance_stage_async(self) -> bool:
        return False

    async def _generate_stages_async(self) -> List[PersonalStage]:
        return [PersonalStage(
            parseable_data=PersonalStageData(
                name="Personal",
                description="",
            ),
            actor_ids=[agent.template.uid for agent in self.scenario.agents],
        )]

    async def assess_scenario_async(self, conversation: Conversation) -> Optional[ScenarioAssessment]:
        return ScenarioAssessment(
            complete=False,
            progress=0,
            reasoning="Personal scenario does not support assessment",
            confidence=0,
        )

