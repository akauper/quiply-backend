import asyncio

from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.conversation_controller import ConversationController, FirstSpeakerMode


class PersonalConversationController(ConversationController):
    @property
    def first_speaker_mode(self) -> FirstSpeakerMode:
        return FirstSpeakerMode.USER

    async def calculate_next_speaking_agent_async(self) -> ScenarioAgent:
        if len(self.scenario.agents) == 1:
            return self.scenario.agents[0]

        # Pair each agent with its corresponding task without starting them
        tasks_with_agents = [(agent, agent.bid_async()) for agent in self.scenario.agents]

        # Start all tasks concurrently and wait for their results
        results = await asyncio.gather(*(task for _, task in tasks_with_agents))

        # Pair each agent with its result and determine the highest bid
        highest_bid = -1
        highest_bid_agent: ScenarioAgent = None
        for agent, result in zip(self.scenario.agents, results):
            print(f"Agent: {agent.character.name}, Bid: {result}")
            if result > highest_bid:
                highest_bid = result
                highest_bid_agent = agent

        print(f"Highest Bid: {highest_bid} from Agent: {highest_bid_agent.character.name}")
        return highest_bid_agent
