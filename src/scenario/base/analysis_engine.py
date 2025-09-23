import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Generic, Type

from devtools import debug

from src.framework import TextGenerator, prompts, TextGenerationParams, Conversation
from src.models import (
    SocialAnalysis,
    ScenarioAnalysis,
    TScenarioSpecificAnalysis,
    ActorFeedback
)
from .component import ScenarioComponent
from ..agents.scenario_agent import ScenarioAgent

if TYPE_CHECKING:
    from .scenario import Scenario


class AnalysisEngine(ScenarioComponent, Generic[TScenarioSpecificAnalysis], ABC):
    generator: TextGenerator

    def __init__(
            self,
            scenario: 'Scenario'
    ) -> None:
        super().__init__(scenario)

        self.generator = TextGenerator(
            process_id=self.instance_uid,
            generation_params=TextGenerationParams(temperature=0)
        )

    @classmethod
    @abstractmethod
    def get_scenario_specific_cls(cls) -> Type[TScenarioSpecificAnalysis]:
        """ This method must be overridden by subclasses to return the concrete class for TScenarioSpecific. """
        raise NotImplementedError

    async def analyze_all_async(
            self,
            conversations: List[Conversation],
    ) -> ScenarioAnalysis:
        conversations_header = f"Start {self.scenario.scenario_name} Transcript"
        conversations_footer = f"End {self.scenario.scenario_name} Transcript"
        if len(conversations) > 1:
            conversations_header += 's'
            conversations_footer += 's'
            conversations_str = Conversation.join_as_string(conversations, omit_system_messages=True)
        else:
            conversations_str = conversations[0].to_string(omit_system_messages=True)

        social_analysis_coroutine = self.analyze_social_skills_async(
            conversations_header=conversations_header,
            conversations_footer=conversations_footer,
            conversations_str=conversations_str,
        )
        scenario_specific_analysis_coroutine = self.analyze_scenario_skills_async(
            conversations_header=conversations_header,
            conversations_footer=conversations_footer,
            conversations_str=conversations_str,
        )
        actor_feedback_coroutines = []
        for agent in self.scenario.agents:
            if len(agent.full_conversation.messages) < 2:
                continue

            debug(agent.full_conversation.to_string(omit_system_messages=True))

            if self.scenario.conversation_controller.separate_agent_conversations:
                conversation_str = agent.full_conversation.to_string(omit_system_messages=True)
            else:
                conversation_str = conversations_str
            actor_feedback_coroutines.append(self._get_actor_feedback(agent, conversation_str))

        all_coroutines = [social_analysis_coroutine, scenario_specific_analysis_coroutine] + actor_feedback_coroutines
        gathered_results = await asyncio.gather(*all_coroutines)

        # Extracting the results
        social_analysis: SocialAnalysis = gathered_results[0]
        scenario_specific_analysis: TScenarioSpecificAnalysis = gathered_results[1]
        actor_feedbacks: List[ActorFeedback] = list(gathered_results[2:])

        debug(actor_feedbacks)

        analysis: ScenarioAnalysis = ScenarioAnalysis(
            social_analysis=social_analysis,
            scenario_specific_analysis=scenario_specific_analysis,
            actor_feedbacks=actor_feedbacks,
        )
        return analysis

    async def analyze_social_skills_async(
            self,
            conversations_header: str,
            conversations_footer: str,
            conversations_str: str,
    ) -> SocialAnalysis:
        format_instructions = SocialAnalysis.get_format_instructions()

        # prompts.analysis.analysis_structure
        prompt = prompts.analysis.analysis_structure
        _input = prompt.format(
            general=self._format_social_analysis_general(),
            conversations_header=conversations_header,
            conversations_footer=conversations_footer,
            conversation_history=conversations_str,
            format_instructions=format_instructions,
        )
        response = await self.generator.run_async(_input)
        debug(response)
        social_analysis: SocialAnalysis = SocialAnalysis.parse(response.content)
        return social_analysis

    def _format_social_analysis_general(self) -> str:
        # social_analysis_instructions
        prompt = prompts.analysis.social_analysis_instructions
        return prompt.format(
            users_name=self.users_name,
            scenario_description=self.scenario.scenario_description,
        )

    async def _get_actor_feedback(self, agent: ScenarioAgent, conversations_str: str) -> ActorFeedback:
        prompt = prompts.analysis.actor_feedback
        _input = prompt.format(
            users_name=self.users_name,
            character_personality=agent.personality,
            conversation_history=conversations_str,
        )

        response = await self.generator.run_async(_input)

        return ActorFeedback(
            actor_uid=agent.template.uid,
            feedback=response.content
        )

    async def analyze_scenario_skills_async(
            self,
            conversations_header: str,
            conversations_footer: str,
            conversations_str: str,
    ) -> TScenarioSpecificAnalysis:
        # Retrieve the concrete class for TScenarioSpecific from the overridden method
        scenario_specific_cls: Type[TScenarioSpecificAnalysis] = self.get_scenario_specific_cls()

        # prompts.analysis.analysis_structure
        prompt = prompts.analysis.analysis_structure
        _input = prompt.format(
            general=self.format_skills_general(),
            conversations_header=conversations_header,
            conversations_footer=conversations_footer,
            conversation_history=conversations_str,
            format_instructions=scenario_specific_cls.get_format_instructions(),
        )
        response = await self.generator.run_async(_input)
        scenario_specific_analysis: TScenarioSpecificAnalysis = scenario_specific_cls.parse(response.content)
        return scenario_specific_analysis

    @abstractmethod
    def format_skills_general(self) -> str:
        pass
