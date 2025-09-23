from typing import List, TYPE_CHECKING, Optional

from src.framework import Conversation
# from src.websocket import ScenarioWsEvents
from src.scenario.base import StageManager
from src.scenario.models import StageFirstSpeakerMode, ScenarioAssessment
from .models import SpeedDatingStageData, SpeedDatingStage

if TYPE_CHECKING:
    from .scenario import SpeedDating


MESSAGE_WARNING_THRESHOLD = 2
TIME_WARNING_THRESHOLD = 60


class SpeedDatingStageManager(StageManager[SpeedDatingStage]):

    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.ALTERNATING

    def __init__(
            self,
            scenario: 'SpeedDating'
    ) -> None:
        super().__init__(scenario, False)

    async def _generate_stages_async(self) -> List[SpeedDatingStage]:
        stages: List[SpeedDatingStage] = []
        for idx, agent in enumerate(self.scenario.agents):
            data = SpeedDatingStageData(
                name=f'Date {idx + 1} with {agent.name}',
                description="",
            )
            stage = SpeedDatingStage(
                parseable_data=data,
                character_uids=[agent.template.uid],
                message_limit=self.settings.stage_message_limit,
                agent_ids=[agent.template.uid],
                # time_limit=self.scenario.max_duration,
            )
            stages.append(stage)
        return stages

    async def check_advance_stage_async(self) -> bool:
        await self.try_send_advisor_comment()

        return self.current_stage.is_over_limit

    async def try_send_advisor_comment(self):
        if self.current_stage.message_limit != 0:
            agent_message_count = len(self.current_stage.agent_messages)
            if self.current_stage.message_limit - agent_message_count == MESSAGE_WARNING_THRESHOLD and not self.current_stage.sent_advisor_message_count_warning:
                self.current_stage.sent_advisor_message_count_warning = True
                # self.websocket_connection.create_scenario_task(ScenarioWsEvents.ADVISOR_COMMENT, data=f'You have {MESSAGE_WARNING_THRESHOLD} messages remaining with this person. Make them count!')
        if self.current_stage.time_limit != 0:
            if self.current_stage.time_remaining < TIME_WARNING_THRESHOLD and not self.current_stage.send_advisor_time_warning:
                self.current_stage.send_advisor_time_warning = True
                # self.websocket_connection.create_scenario_task(ScenarioWsEvents.ADVISOR_COMMENT, data='You have 1 minute remaining with this person. Make it count!')

    async def assess_scenario_async(self, conversation: Conversation) -> Optional[ScenarioAssessment]:
        if self.completed_all_stages:
            return ScenarioAssessment(
                complete=True,
                progress=1,
                confidence=1,
                reasoning="Went on a date with everyone!"
            )
        else:
            progress_percent = max(self.current_stage.time_progress or 0, self.current_stage.message_progress or 0)
            progress_percent = max(0, min(1, progress_percent))
            return ScenarioAssessment(
                complete=False,
                progress=progress_percent,
                confidence=1,
                reasoning="Still have more dates to go!"
            )
    # async def check_completion_async(
    #         self,
    #         message_history: List[QMessage] | str,
    #         verbose: bool = False
    # ) -> ScenarioCompleteState:
    #     if self.completed_all_stages:
    #         return ScenarioCompleteState(
    #             complete=True,
    #             confidence=1,
    #             reasoning="Went on a date with everyone!"
    #         )
    #     else:
    #         return ScenarioCompleteState(
    #             complete=False,
    #             confidence=0,
    #             reasoning="Still have more dates to go!"
    #         )
    #
    # async def check_progress_async(
    #         self,
    #         message_history: List[QMessage] | str,
    #         verbose: bool = False
    # ) -> Progress | None:
    #     progress_percent = max(self.current_stage.time_progress or 0, self.current_stage.message_progress or 0)
    #     progress_percent = max(0, min(1, progress_percent))
    #
    #     return Progress(
    #         progress=progress_percent,
    #         reasoning=""
    #     )
