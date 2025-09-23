from typing import List, TYPE_CHECKING, Optional

from src.framework import prompts, Conversation, NumberedListPostProcessor
# from src.websocket import ScenarioWsEvents
from src.scenario.base import StageManager
from src.scenario.models import StageFirstSpeakerMode, ScenarioAssessment, TScenarioStage
from src.utils import list_to_comma_delimited_str
from .models import DebateStage, DebateStageData

if TYPE_CHECKING:
    from .scenario import Debate


MESSAGE_WARNING_THRESHOLD = 1
TIME_WARNING_THRESHOLD = 30


class DebateStageManager(StageManager[DebateStage]):

    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.ALTERNATING

    def __init__(
            self,
            scenario: 'Debate'
    ) -> None:
        super().__init__(scenario, False)

    async def _generate_stages_async(self) -> List[DebateStage]:
        stages: List[DebateStage] = []
        questions = await self.generate_debate_questions()

        max_rounds = min(len(questions), self.settings.stage_count)
        for index, question in enumerate(questions[:max_rounds], start=1):
            data: DebateStageData = DebateStageData(
                name=f"Round {index}",
                description=f"Round {index} discussion",
                question=question,
            )
            stages.append(DebateStage(
                parseable_data=data,
                character_uids=[agent.template.uid for agent in self.scenario.agents],
                message_limit=self.settings.stage_message_limit,
                # time_limit=self.scenario.round_time_limit,
            ))
        return stages

    async def generate_debate_questions(self) -> List[str]:
        post_processor = NumberedListPostProcessor()

        format_instructions = post_processor.get_generator_instructions_str()

        response = await self._generate_debate_questions_raw(format_instructions)
        response_list = post_processor.run(response)
        return response_list

    async def _generate_debate_questions_raw(self, format_instructions: str) -> str:
        participants = [self.users_name] + [agent.name for agent in self.scenario.agents]
        participants_str = list_to_comma_delimited_str(participants)

        prompt = prompts.debate.character.generate_questions
        _input = prompt.format(
            topic=self.settings.topic,
            participants=participants_str,
            question_count=self.settings.stage_message_limit,
            format_instructions=format_instructions
        )
        response = await self.generator.run_async(_input)
        self.loggers.llm.info(f'GENERATE QUESTIONS RESPONSE: {response.content}')
        return response.content

    async def check_advance_stage_async(self) -> bool:
        await self.try_send_advisor_comment()

        return self.current_stage.is_over_limit

    async def try_send_advisor_comment(self):
        if self.current_stage.message_limit != 0:
            message_count = self.current_stage.agent_message_count if self.current_stage.first_speaker_type == 'ai' else self.current_stage.user_message_count
            if self.current_stage.message_limit - message_count == MESSAGE_WARNING_THRESHOLD and not self.current_stage.sent_advisor_message_count_warning:
                self.current_stage.sent_advisor_message_count_warning = True
                # await self.scenario.websocket_connection.send_scenario_async(ScenarioWsEvents.ADVISOR_COMMENT, data='These are your last message for this question. Make it count!')
        if self.current_stage.time_limit != 0:
            if self.current_stage.time_remaining < TIME_WARNING_THRESHOLD and not self.current_stage.send_advisor_time_warning:
                self.current_stage.send_advisor_time_warning = True
                # await self.scenario.websocket_connection.send_scenario_async(ScenarioWsEvents.ADVISOR_COMMENT, data=f'You have {TIME_WARNING_THRESHOLD} seconds remaining on this question. Make it count!')

    async def assess_scenario_async(self, conversation: Conversation) -> Optional[ScenarioAssessment]:
        if self.completed_all_stages:
            return ScenarioAssessment(
                complete=True,
                progress=1,
                confidence=1,
                reasoning="All stages completed",
            )
        else:
            progress_percent = max(self.current_stage.time_progress or 0, self.current_stage.message_progress or 0)
            progress_percent = max(0, min(1, progress_percent))
            return ScenarioAssessment(
                complete=False,
                progress=progress_percent,
                confidence=1,
                reasoning="Not all stages completed",
            )

    # async def check_completion_async(
    #         self,
    #         message_history: List[QMessage] | str,
    #         verbose: bool = False
    # ) -> ScenarioCompleteState:
    #     if self.completed_all_stages:
    #         return ScenarioCompleteState(complete=True, confidence=1, reasoning="All stages completed")
    #     else:
    #         return ScenarioCompleteState(complete=False, confidence=1, reasoning="Not all stages completed")
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
