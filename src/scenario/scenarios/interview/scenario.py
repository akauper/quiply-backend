from src.framework import prompts
from src.scenario.base import Scenario
from src.utils import loggers
from .agent_builder import InterviewAgentBuilder
from .analysis_engine import InterviewAnalysisEngine
from .conversation_controller import InterviewConversationController
from .stage_manager import InterviewStageManager


class Interview(Scenario):
    def _init_params(self):
        self.params.company_name = self.scenario_config.field_values['company_name']
        self.params.job_title = self.scenario_config.field_values['job_title']

        if self.params.duration is None:
            self.params.stage_message_limit = 10
        else:
            duration = self.params.duration.lower()
            if duration == 'short':
                self.params.stage_message_limit = 7
            elif duration == 'medium':
                self.params.stage_message_limit = 11
            elif duration == 'long':
                self.params.stage_message_limit = 16
            else:
                loggers.scenario.warning(f"Invalid duration value: {duration}. Setting to default values.")
                self.params.stage_message_limit = 10

    def _parse_difficulty_description(self, difficulty: str) -> None:
        pass

    def create_conversation_controller(self):
        return InterviewConversationController(scenario=self)

    def create_agent_builder(self):
        return InterviewAgentBuilder(scenario=self)

    def create_analysis_engine(self):
        return InterviewAnalysisEngine(scenario=self)

    def create_stage_manager(self):
        return InterviewStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "You're interviewer will be with you shortly."

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"The following is IMPORTANT additional information about the interview: {context}"

        prompt = prompts.interview.description
        formatted = prompt.format(
            job_title=self.params.job_title,
            company_name=self.params.company_name,
            character_name=self.agents[0].name,
            users_name=self.users_name,
            additional_scenario_context=additional_scenario_context,
        )
        return formatted
