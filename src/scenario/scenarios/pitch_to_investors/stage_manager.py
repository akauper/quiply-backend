from typing import List, Optional

from src.framework import Conversation
from src.scenario.base import StageManager
from .models import PitchToInvestorsStage, PitchToInvestorsStageData
from src.scenario.models import StageFirstSpeakerMode, ScenarioAssessment


class PitchToInvestorsStageManager(StageManager[PitchToInvestorsStage]):
    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.USER_ALWAYS_FIRST

    async def check_advance_stage_async(self) -> bool:
        return self.current_stage.is_over_message_limit

    async def _generate_stages_async(self) -> List[PitchToInvestorsStage]:
        return [PitchToInvestorsStage(
            parseable_data=PitchToInvestorsStageData(
                name="Pitch to Investors",
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
            reasoning="Pitch to Investors scenario does not support assessment",
            confidence=0,
        )