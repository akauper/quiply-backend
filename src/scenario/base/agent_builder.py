from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING, Callable, Tuple

from devtools import debug

from src._debug import quiply_debug
from src.framework import prompts, TextGenerator, TextGenerationParams, Message, AgentParams, PromptMessage, Prompt, \
    MessageRole
from src.services import storage_service
from src.utils import add_tab_to_each_line, list_to_comma_delimited_str
from .component import ScenarioComponent
from .. import ScenarioAgent
from ..models import AgentType
from ...models.schemas import TActorComponent

if TYPE_CHECKING:
    from .scenario import Scenario


class AgentBuilder(ScenarioComponent, ABC):
    _summarize_personalities: bool

    generator: TextGenerator

    def __init__(
            self,
            scenario: 'Scenario',
    ) -> None:
        super().__init__(scenario)

        try:
            self.generator = TextGenerator(
                process_id=self.instance_uid,
                generation_params=TextGenerationParams(
                    temperature=0.4
                )
            )

            self._summarize_personalities = self.scenario_template.actor_settings.summarize_actor_personalities
            self.scenario.agents = self.build_agents()
            self.scenario.special_agents = self.build_special_agents()
            # self.scenario.mentor = self.build_mentor()
        except Exception as e:
            raise e

    async def awake(self):
        await self.initialize_agents(self.scenario.agents)
        await self.initialize_agents(self.scenario.special_agents)
        # await self.initialize_agents([self.scenario.mentor])

    def build_agents(self) -> List[ScenarioAgent]:
        agents = []

        # Create all agents
        for actor_id in self.scenario_config.actor_ids:
            template = storage_service.get_actor_template(actor_id)
            agent = ScenarioAgent(
                process_id=self.instance_uid,
                template=template,
                scenario=self.scenario,
                verbose=True)
            agents.append(agent)

        # Add agent prefixes to stop list
        prefixes = [agent.prefix for agent in agents]
        for agent in agents:
            agent.text_generator.generation_params.add_stop(prefixes + [self.scenario.users_prefix])

            if len(self.scenario.settings.agent_callbacks) > 0:
                agent.runnable_params.callbacks += self.scenario.settings.agent_callbacks
        return agents

    def build_special_agents(self) -> List[ScenarioAgent]:
        special_agents = []
        for special_actor_id in self.scenario_config.special_actor_ids:
            template = storage_service.get_actor_template(special_actor_id)
            agent = ScenarioAgent(
                process_id=self.instance_uid,
                template=template,
                type=AgentType.SPECIAL_AGENT,
                scenario=self.scenario,
                verbose=True
            )
            special_agents.append(agent)
        return special_agents

    def build_mentor(self) -> ScenarioAgent:
        mentor_template = storage_service.get_mentor_template(self.scenario_template.advisor_uid)
        return ScenarioAgent(
            process_id=self.instance_uid,
            template=mentor_template,
            type=AgentType.MENTOR,
            scenario=self.scenario,
            verbose=True
        )

    async def initialize_agents(self, agents: List[ScenarioAgent]) -> None:
        for agent in agents:
            personality = None

            if agent.type == AgentType.AGENT:
                system_message, personality = await self.format_system_message_async(agent)
            elif agent.type == AgentType.SPECIAL_AGENT:
                system_message = await self.format_special_actor_system_message_async(agent)
            elif agent.type == AgentType.MENTOR:
                system_message = self.get_advisor_system_message(agent)
            else:
                raise ValueError(f"Unknown agent type: {agent.type}")

            agent.add_message(system_message)
            if personality is not None:
                agent.personality = personality

    async def format_system_message_async(self, agent: ScenarioAgent) -> Tuple[Message, str]:
        """Generates final system message for the ScenarioAgent"""

        common_instructions = self.get_common_instructions(agent)
        scenario_instructions = self.get_scenario_instructions(agent)
        scenario_additional_information = self.scenario.get_additional_scenario_information()
        role_and_behaviour = self.get_role_and_behaviour(agent)
        personality = add_tab_to_each_line(await self.get_actor_personality_async(agent))
        # scenario_specific_personality_traits = self.get_scenario_specific_personality_traits(agent)
        extra_information = await self.get_extra_information_async(
            agent,
            scenario_instructions,
            scenario_additional_information,
            role_and_behaviour,
            personality
        )

        prompt = prompts.character.system_message_structure

        return PromptMessage(
            role=MessageRole.system,
            author_id=agent.id,
            author_name=agent.name,
            scenario_instance_id=self.scenario.instance.uid,
            prompt=prompt,
            input_variables={
                'scenario_name': self.scenario.scenario_name,
                'character_name': agent.name,
                'common_instructions': lambda: self.get_common_instructions(agent),
                'scenario_instructions': lambda: add_tab_to_each_line(self.get_scenario_instructions(agent)),
                'scenario_additional_information': lambda: self.scenario.get_additional_scenario_information(),
                'role_and_behavior': lambda: self.get_role_and_behaviour(agent),
                'personality': personality,
                'scenario_specific_personality_traits': lambda: add_tab_to_each_line(self.get_scenario_specific_personality_traits(agent)),
                'extra_information': extra_information,
            }
        ), personality

    def get_common_instructions(self, agent: ScenarioAgent) -> str:
        return prompts.character.common_instructions.get_prompt().template

    @abstractmethod
    def get_scenario_instructions(self, agent: ScenarioAgent) -> str:
        pass

    @abstractmethod
    def get_role_and_behaviour(self, agent: ScenarioAgent) -> str:
        pass

    @abstractmethod
    def get_scenario_specific_personality_traits(self, agent: ScenarioAgent) -> str:
        pass

    async def get_actor_personality_async(self, agent: ScenarioAgent) -> str:
        if (debug_personality := quiply_debug.get_personality(self.template_uid)) is not None:
            return debug_personality

        actor = agent.template
        components = self.scenario_template.actor_settings.get_actor_components(actor)
        actor_traits = "\n" + "\n\t".join([self.format_actor_component(component) for component in components])

        prompt = prompts.character.personality

        if self._summarize_personalities:
            common_personality = await self.summarize_agent_personality_async(
                common_personality=actor.profile,
                traits=actor_traits,
                agent=agent
            )
            formatted = prompt.format(
                common_personality=add_tab_to_each_line(common_personality, True),
                traits="",
                additional_information=self.get_additional_actor_information(agent)
            )
        else:
            formatted = prompt.format(
                common_personality=actor.profile,
                traits=actor_traits,
                additional_information=self.get_additional_actor_information(agent)
            )

        return formatted

    def format_actor_component(self, component: TActorComponent):
        """We break this out so that scenarios can override this method to customize the formatting of actor components"""
        return component.format()

    async def summarize_agent_personality_async(self, common_personality: str, traits: str, agent: ScenarioAgent) -> str:
        """Override this method to adapt the personality profile to the role of the agent"""

        prompt = prompts.character.summarize_personality
        _input = prompt.format(
            character_name=agent.name,
            common_personality=common_personality,
            traits=traits
        )
        response = await self.generator.run_async(_input)

        return f"""\t{response.content}"""

    def get_additional_actor_information(self, agent: ScenarioAgent) -> str:
        additional_information: str = self.scenario_config.get_actor_additional_information(
            agent.template.uid
        )
        if additional_information is not None and additional_information != "":
            return f"""The following is IMPORTANT additional information about {agent.name}: {additional_information}"""
        return ""

    async def get_extra_information_async(
            self,
            agent: ScenarioAgent,
            scenario_instructions: str,
            scenario_additional_information: str,
            role_and_behaviour: str,
            personality: str,
    ) -> str:
        """Override this method to add extra information to the agent's system message"""
        return ""

    def get_advisor_system_message(self, advisor: ScenarioAgent) -> Message:
        agent_names = self.get_agent_names_str()

        prompt = prompts.mentor.system_message_structure

        def get_user_conversation():
            messages = self.scenario.conversation_controller.current_conversation.messages
            messages = [message for message in messages if message.role is not MessageRole.system]
            return Message.join_as_string(messages)

        return PromptMessage(
            role=MessageRole.system,
            author_id=advisor.id,
            author_name=advisor.name,
            scenario_instance_id=self.scenario.instance.uid,
            prompt=prompt,
            input_variables={
                'advisor_name': advisor.name,
                'users_name': self.users_name,
                'actor_names': agent_names,
                'scenario_name': self.scenario.scenario_name,
                'scenario_description': self.scenario.scenario_description,
                'user_conversation': get_user_conversation,
            },
        )
        # return Message.from_system(
        #     content=_input,
        #     scenario_instance_id=self.scenario.instance_uid,
        # )

    async def format_special_actor_system_message_async(self, agent: ScenarioAgent) -> Message:
        return Message.from_system(
            content='',
            author_id=agent.id,
            author_name=agent.name,
            scenario_instance_id=self.scenario.instance_uid,
        )

    def get_agents_without_name(self, name: str) -> List[ScenarioAgent]:
        return [agent for agent in self.scenario.agents if agent.template.name != name]

    def get_agent_names_str(self) -> str:
        agents_name_list = [agent.name for agent in self.scenario.agents]
        return list_to_comma_delimited_str(agents_name_list)

