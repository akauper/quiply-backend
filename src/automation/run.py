import asyncio
from typing import List, Optional

from .conversation import AutoConversation, AutoConversationConfig
from ..framework import BaseAsyncCallback, Message


def run_automations():
    asyncio.create_task(run_automations_async())


async def run_automations_async():
    # Placeholder for any automations we want to do.
    await run_conversations()
    pass


class TestCallback(BaseAsyncCallback):
    async def on_agent_generation_end(
        self,
        info: "RunInfo",
        *,
        response: Message,
        agent: Optional["Agent"] = None,
        message_list: Optional[List[Message]] = None,
        **kwargs,
    ):
        print(f"TestCallback: on_agent_generation_end: {response.content}")


async def run_conversations():
    callbacks: List[TestCallback] = [TestCallback()]

    config = AutoConversationConfig(
        auto_user_template_id="frank",
        scenario_template_id="pitch_to_investors",
        scenario_name="Pitch To Investors",
        message_count=1,
        agent_callbacks=callbacks,
    )
    auto_conversation = AutoConversation(config)
    output = await auto_conversation.run_async()
    output.save()
