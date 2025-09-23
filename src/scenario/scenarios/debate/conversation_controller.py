import asyncio

from src.framework import prompts, EvaluablePrompt
from src.scenario.agents.scenario_agent import ScenarioAgent
from src.scenario.base.conversation_controller import ConversationController, FirstSpeakerMode
from src.scenario.scenarios.debate.models import DebateStage


class DebateConversationController(ConversationController):

    @property
    def first_speaker_mode(self) -> FirstSpeakerMode:
        return FirstSpeakerMode.USER

    def send_first_message(self):
        if self.settings.stage_message_limit and self.settings.stage_message_limit != 0:
            constraints = f"{self.settings.stage_message_limit} messages"
        else:
            constraints = ""

        if self.first_speaker == 'user':
            first_speaker_name = self.users_name
        else:
            first_speaker_name = self.current_speaking_agent.character.name

        prompt = prompts.debate.moderator.intro

        content = prompt.format(
            topic=self.settings.topic,
            constraints=constraints,
            first_speaker=first_speaker_name,
            question=self.scenario.stage_manager.current_stage.parseable_data.question,
        )
        self.scenario.create_task(self.scenario.moderator.send_pregenerated_message(content, is_moderator=True))

        super().send_first_message()

    def on_stage_change(self, stage: DebateStage):
        self.loggers.stage.info(f"Stage: {stage}")
        try:
            if stage.first_speaker_type == "user":
                speaker_name = self.users_name
            else:
                speaker_name = self.scenario.agents[stage.first_speaker_agent_index].name

            prompt = prompts.debate.moderator.next_stage

            content = prompt.format(
                question=stage.question,
                next_speaker=speaker_name,
            )
            self.scenario.create_task(self.scenario.moderator.send_pregenerated_message(content, is_moderator=True))

            super().on_stage_change(stage)
        except Exception as e:
            self.loggers.stage.exception(e)
            raise e

    async def calculate_next_speaking_agent_async(self) -> ScenarioAgent:
        if len(self.scenario.agents) == 1:
            return self.scenario.agents[0]

        prompt: EvaluablePrompt = prompts.debate.bid

        # Pair each agent with its corresponding task without starting them
        tasks_with_agents = [(agent, agent.bid_async(prompt=prompt.get_prompt())) for agent in self.scenario.agents]

        # Start all tasks concurrently and wait for their results
        results = await asyncio.gather(*(task for _, task in tasks_with_agents))

        # Pair each agent with its result and determine the highest bid
        highest_bid = -1
        highest_bid_agent: ScenarioAgent | None = None
        for agent, result in zip(self.scenario.agents, results):
            print(f"Agent: {agent.character.name}, Bid: {result}")
            if result > highest_bid:
                highest_bid = result
                highest_bid_agent = agent

        print(f"Highest Bid: {highest_bid} from Agent: {highest_bid_agent.character.name}")
        return highest_bid_agent
