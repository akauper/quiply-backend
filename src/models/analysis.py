from abc import ABC
from typing import List, Optional, TypeVar, Any

from pydantic import BaseModel, Field

from .base import SerializableObject, ParseableModel


class Metric(BaseModel):
    score: float = Field(default=0.0, description="A floating-point value between 0.0 and 1.0 that reflects the score for this metric")
    notes: str = Field(default="", description="Notes on the score. Why the score was given")
#
#
# class SummaryAndAdvice(BaseModel):
#     overall_score: float = Field(default=0.0)
#     overall_impression: str = Field(default="", description="This should be a short paragraph with your overall impression of the user's interview performance. At least 4 sentences.")
#     advice_for_improvement: List[str] = Field(default_factory=list, description="List of strings that give advice on how to improve")
#     areas_of_excellence: List[str] = Field(default_factory=list, description="List of strings that give feedback on what the user did well")
#
#
# class Analysis(ParseableModel, ABC):
#     summary_and_advice: SummaryAndAdvice = Field(default_factory=SummaryAndAdvice)
#     llm_completion_info: Optional[LLMCompletionInfo] = None
#
#
# class CommunicationSkills(BaseModel):
#     clarity_and_conciseness: Metric = Field(default_factory=Metric, description="Were the person's points made in a manner that was easily understood? Did they get to the point quickly?")
#     grammar_and_vocabulary: Metric = Field(default_factory=Metric, description="Did the person use of language appropriate for the setting? Did any language barriers impede communication?")
#     tone_and_style: Metric = Field(default_factory=Metric, description="Did the person adjust their style of communication to suit the scenario or the people they were interacting with?")
#
#
# class InterpersonalSkills(BaseModel):
#     rapport_building: Metric = Field(default_factory=Metric, description="Did the person attempt to make meaningful connections? Were they effective in doing so?")
#     active_listening: Metric = Field(default_factory=Metric, description="Was the person attentive and did they give appropriate responses indicating they were engaged?")
#     empathy_and_understanding: Metric = Field(default_factory=Metric, description="Were there instances where the person showed a keen understanding of other people's emotions or perspectives?")
#
#
# class ConfidenceAndAssertiveness(BaseModel):
#     self_presentation: Metric = Field(default_factory=Metric, description="How well did the person present themselves? Was their demeanor suitable for the scenario?")
#     handling_criticism: Metric = Field(default_factory=Metric, description="Was the person receptive to feedback, or did they become defensive?")
#
#
# class BehavioralIndicators(BaseModel):
#     positivity: Metric = Field(default_factory=Metric, description="Was the person a generally positive influence in the scenario?")
#     initiative: Metric = Field(default_factory=Metric, description="Did the person take control of the situation when needed, without dominating others?")
#
#
# class SocialAnalysis(Analysis):
#     communication_skills: CommunicationSkills = Field(default_factory=CommunicationSkills)
#     interpersonal_skills: InterpersonalSkills = Field(default_factory=InterpersonalSkills)
#     confidence_and_assertiveness: ConfidenceAndAssertiveness = Field(default_factory=ConfidenceAndAssertiveness)
#     behavioral_indicators: BehavioralIndicators = Field(default_factory=BehavioralIndicators)
#
#
# class ScenarioSpecificAnalysis(Analysis):
#     # scenario_template_id: str = Field(default="")
#     pass

'''
collaboration: Metric = Field(default_factory=Metric, description="Evaluate the user's ability to work effectively in a group setting, focusing on their cooperation, contribution to collective tasks, and ability to support and enhance group dynamics.")
leadership: Metric = Field(default_factory=Metric, description="Evaluate the user's ability to lead and guide others in various social contexts. Focus on assessing their skills in inspiring and motivating people, decision-making, delegating responsibilities, and guiding a group towards achieving common goals.")
depth_of_knowledge: Metric = Field(default_factory=Metric, description="Assess the user's level of knowledge and expertise in specific topics discussed during social interactions. Provide feedback on how well they understand and convey complex ideas, and how effectively they use their knowledge to contribute to meaningful discussions.")
'''


class SocialAnalysis(ParseableModel):
    overall_score: float = Field(default=0.0, description="A floating-point value between 0.0 and 1.0 that reflects the overall score of the user.")
    overall_impression: str = Field(default="", description="This should be a short paragraph with your overall impression of the user's interview performance. At least 4 sentences.")
    areas_for_improvement: List[str] = Field(default_factory=list, description="List of strings that explains to the person what they need to improve on. Do not give advice here. Just say what they didn't do well.")
    areas_of_excellence: List[str] = Field(default_factory=list, description="List of strings that give explains to the person what they did well.")
    growth_strategies: List[str] = Field(default_factory=list, description="List of strings that give feedback on what the person can do to improve.")

    emotional_intelligence: Metric = Field(default_factory=Metric, description="Grasp on emotional nuances, reflecting their ability to interpret and manage personal emotions, and to sensitively navigate the emotions of others in various social situations.")
    active_listening: Metric = Field(default_factory=Metric, description="Listening abilities, capturing their engagement in conversations through understanding, reflecting, and responding to what others say, beyond mere hearing.")
    effective_communication: Metric = Field(default_factory=Metric, description="Proficiency in expressing ideas and feelings, as well as comprehending others' messages. This encompasses clarity in verbal expression, appropriate use of non-verbal cues, and the overall effectiveness in exchanging information.")
    social_awareness: Metric = Field(default_factory=Metric, description="Sensitivity to the social environment, including an awareness of social dynamics, empathy towards others' emotions, and the ability to navigate social interactions with understanding and tact.")

    confidence: Metric = Field(default_factory=Metric, description="Self-assuredness and assertiveness in social settings, reflecting their level of comfort and poise in expressing themselves and interacting with others.")
    conflict_resolution: Metric = Field(default_factory=Metric, description="Capabilities in addressing and resolving disagreements, focusing on their approach to understanding different perspectives, negotiating solutions, and maintaining constructive interactions.")
    adaptability: Metric = Field(default_factory=Metric, description="Ability to effectively adjust to varied social environments and situations, highlighting flexibility in approach and openness to change in interpersonal interactions.")
    persuasion_and_influence: Metric = Field(default_factory=Metric, description="Ability to sway or impact others' viewpoints, emphasizing their skill in articulating persuasive arguments, inspiring action, and effectively influencing the opinions and behaviors of others.")


class ScenarioSpecificAnalysis(ParseableModel, ABC):
    pass


TScenarioSpecificAnalysis = TypeVar('TScenarioSpecificAnalysis', bound=ScenarioSpecificAnalysis)


class ActorFeedback(BaseModel):
    actor_uid: str
    feedback: str


class ScenarioAnalysis(SerializableObject):
    social_analysis: SocialAnalysis
    scenario_specific_analysis: TScenarioSpecificAnalysis
    actor_feedbacks: List[ActorFeedback] = Field(default_factory=list)

    llm_completion_info: Optional[Any] = None
