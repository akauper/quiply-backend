from src.scenario.base.conversation_controller import ConversationController, FirstSpeakerMode
from src.scenario.agents.scenario_agent import ScenarioAgent


class InterviewConversationController(ConversationController):
    @property
    def first_speaker_mode(self) -> FirstSpeakerMode:
        return FirstSpeakerMode.AI

    async def calculate_next_speaking_agent_async(self) -> ScenarioAgent:
        return self.scenario.agents[0]
