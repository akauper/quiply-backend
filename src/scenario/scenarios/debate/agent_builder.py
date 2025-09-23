from src.framework import prompts, Message
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base import AgentBuilder
from src.utils import list_to_comma_delimited_str


class DebateAgentBuilder(AgentBuilder):

    def format_topic(self) -> str:
        if self.settings.topic:
            return f" about {self.settings.topic}"
        else:
            return ""

    async def format_special_actor_system_message_async(self, agent: ScenarioAgent) -> Message:
        other_participant_names = [name for name in self.scenario.participant_names if name != agent.name]
        other_participant_names_str = list_to_comma_delimited_str(other_participant_names)

        prompt = prompts.debate.moderator.system_message
        formatted = prompt.format(
            character_name=agent.name,
            topic=self.format_topic(),
            other_character_names=other_participant_names_str
        )
        return Message.from_system(
            content=formatted,
            author_id=agent.id,
            author_name=agent.name,
            scenario_instance_id=self.scenario.instance_uid,
        )

    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        other_participant_names = [name for name in self.scenario.participant_names if name != agent.name]
        other_participant_names_str = list_to_comma_delimited_str(other_participant_names)

        prompt = prompts.debate.character.instructions
        return prompt.format(
            character_name=agent.name,
            topic=self.format_topic(),
            other_character_names=other_participant_names_str,
            moderator_name=self.scenario.moderator.name,
        )

    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        prompt = prompts.debate.character.role_and_behaviour

        return prompt.format(
            character_name=agent.name,
            users_name=self.users_name,
        )

    def get_advisor_scenario_description(self) -> str:
        return f"a debate{self.format_topic()}"
