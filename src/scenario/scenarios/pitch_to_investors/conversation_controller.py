from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.conversation_controller import ConversationController, FirstSpeakerMode


class PitchToInvestorsConversationController(ConversationController):
    @property
    def first_speaker_mode(self) -> FirstSpeakerMode:
        return FirstSpeakerMode.USER

    async def calculate_next_speaking_agent_async(self) -> ScenarioAgent:
        return self.scenario.agents[0]
