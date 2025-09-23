from typing import List

from src.framework import prompts, TextGenerationParams, TextGenerator
from src.scenario.base import StageManager
from src.scenario.models import StageFirstSpeakerMode
from .models import InterviewStage, InterviewStageDataList


class InterviewStageManager(StageManager[InterviewStage]):

    @property
    def stage_first_speaker_mode(self) -> StageFirstSpeakerMode:
        return StageFirstSpeakerMode.USER_ALWAYS_FIRST

    async def check_advance_stage_async(self) -> bool:
        return False

    async def _generate_stages_async(self) -> List[InterviewStage]:
        # generation_params = TextGenerationParams(
        #     temperature=0,
        #     max_tokens=500
        # )
        generator = TextGenerator(process_id=self.instance_uid, temperature=0, max_tokens=500)

        stage_datas_list_cls = InterviewStageDataList
        # print(stage_datas_list_cls.get_format_instructions())
        prompt = prompts.interview.stages
        _input = prompt.format(
            scenario_description=self.scenario.scenario_description,
            format_instructions=stage_datas_list_cls.get_format_instructions()
        )

        response = await generator.run_async(_input)
        # print('generate stages response', response)

        stage_data_list: stage_datas_list_cls = stage_datas_list_cls().parse(response.content)
        stages: List[InterviewStage] = []
        for stage_data in stage_data_list.stage_datas:
            stage = InterviewStage(
                parseable_data=stage_data,
                character_uids=[agent.template.uid for agent in self.scenario.agents],
                message_limit=self.settings.stage_message_limit,
            )
            stages.append(stage)
        return stages
