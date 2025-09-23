from typing import List, Optional

from src.framework import Conversation
from src.scenario.base import StageManager
from .models import SellMeThisPenStage, SellMeThisPenStageData
from src.scenario.models import StageFirstSpeakerMode, ScenarioAssessment


class SellMeThisPenStageManager(StageManager[SellMeThisPenStage]):
    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.USER_ALWAYS_FIRST

    async def check_advance_stage_async(self) -> bool:
        return self.current_stage.is_over_message_limit

    async def _generate_stages_async(self) -> List[SellMeThisPenStage]:
        return [SellMeThisPenStage(
            parseable_data=SellMeThisPenStageData(
                name="Sell Me  This Pen",
                description="",
            ),
            character_uids=[agent.template.uid for agent in self.scenario.agents],
            message_limit=self.settings.stage_message_limit,
            # time_limit=self.scenario.time_limit,
        )]

    async def assess_scenario_async(self, conversation: Conversation) -> Optional[ScenarioAssessment]:
        return ScenarioAssessment(
            complete=False,
            progress=0,
            reasoning="Sell Me This Pen scenario does not support assessment",
            confidence=0,
        )