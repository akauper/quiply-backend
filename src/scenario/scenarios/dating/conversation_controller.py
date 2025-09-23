from typing import TYPE_CHECKING

# from src.websocket import ScenarioWsEvents, ScenarioNotification
from src.scenario.base.conversation_controller import ConversationController, FirstSpeakerMode
from src.utils import logger

if TYPE_CHECKING:
    from .scenario import Scenario


class DatingConversationController(ConversationController):

    @property
    def first_speaker_mode(self) -> FirstSpeakerMode:
        return FirstSpeakerMode.AI

    def __init__(
            self,
            scenario: 'Scenario',
    ) -> None:
        super().__init__(scenario)
        self.separate_agent_conversations = True

    def send_first_message(self):
        if self.first_speaker == 'user':
            pass
            # self.websocket_connection.create_scenario_task(ScenarioWsEvents.NOTIFICATION, data=ScenarioNotification.AWAIT_USER_MESSAGE())
        else:
            agent_id = self.scenario.stage_manager.current_stage.agent_ids[0]
            agent = next((a for a in self.scenario.agents if a.template.uid == agent_id), None)
            self.generate_agent_message(agent)

    async def calculate_next_speaking_agent_async(self) -> None:
        agent_id = self.scenario.stage_manager.current_stage.agent_ids[0]
        agent = next((a for a in self.scenario.agents if a.template.uid == agent_id), None)
        if agent is not None:
            self.current_speaking_agent = agent
        else:
            logger.exception(f"Could not find agent with uid {agent_id}")
