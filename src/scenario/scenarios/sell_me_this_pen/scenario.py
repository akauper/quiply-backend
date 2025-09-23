from devtools import debug


from src.framework import prompts
from src.scenario.base.scenario import Scenario
from src.utils import loggers
from .agent_builder import SellMeThisPenAgentBuilder
from .analysis_engine import SellMeThisPenAnalysisEngine
from .conversation_controller import SellMeThisPenConversationController
from .stage_manager import SellMeThisPenStageManager


class SellMeThisPen(Scenario):
    def _init_params(self):
        super()._init_params()
        debug(self.scenario_config)
        self.params.audience = self.scenario_config.field_values.get("audience", None)
        self.params.selling = self.scenario_config.field_values.get("selling", None)
        self.params.location = self.scenario_config.field_values.get("location", None)

        if self.params.duration is None:
            self.params.stage_message_limit = 7
        else:
            duration = self.params.duration.lower()
            if duration == "short":
                self.params.stage_message_limit = 5
            elif duration == "medium":
                self.params.stage_message_limit = 7
            elif duration == "long":
                self.params.stage_message_limit = 12
            else:
                loggers.scenario.warning(
                    f"Invalid duration value: {duration}. Setting to default values."
                )
                self.params.stage_message_limit = 5

    def create_conversation_controller(self) -> SellMeThisPenConversationController:
        return SellMeThisPenConversationController(scenario=self)

    def create_agent_builder(self) -> SellMeThisPenAgentBuilder:
        return SellMeThisPenAgentBuilder(scenario=self)

    def create_analysis_engine(self) -> SellMeThisPenAnalysisEngine:
        return SellMeThisPenAnalysisEngine(scenario=self)

    def create_stage_manager(self) -> SellMeThisPenStageManager:
        return SellMeThisPenStageManager(scenario=self)

    def get_initializing_message(self) -> str:
        return "The investors will arrive soon."

    def _format_scenario_description(self) -> str:
        additional_scenario_context = ""
        context = self.scenario_config.scenario_additional_information
        if context is not None:
            additional_scenario_context = f"""The following is IMPORTANT additional information about the pitch: {context}
            This may include details like the setting of the pitch (e.g., a casual meeting, a formal investor gathering), the main objectives of the pitcher, and specific interests or concerns of the listener."""

        prompt = prompts.sell_me_this_pen.scenario_description
        formatted = prompt.format(
            users_name=self.users_name,
            selling=self.params.selling,
            audience=self.params.audience,
            location=self.params.location,
            additional_scenario_context=additional_scenario_context,
        )

        # if len(self.agents) > 1:
        #     agent_name_list = [agent.name for agent in self.agents]
        #     audience_names = list_to_comma_delimited_str(agent_name_list)
        #     prompt = prompts.pitch_to_investors.group_investor_description
        # else:
        #     audience_names = self.agents[0].name
        #     prompt = prompts.pitch_to_investors.single_investor_description
        #
        # additional_scenario_context = ""
        # context = self.scenario_config.scenario_additional_information
        # if context is not None:
        #     additional_scenario_context = f"""The following is IMPORTANT additional information about the pitch: {context}
        #     This may include details like the setting of the pitch (e.g., a casual meeting, a formal investor gathering), the main objectives of the pitcher, and specific interests or concerns of the listener."""
        # formatted = prompt.format(
        #     audience_names=audience_names,
        #     audience_type=self.settings.audience_type,
        #     users_name=self.users_name,
        #     additional_scenario_context=additional_scenario_context
        # )

        return formatted
