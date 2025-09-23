import asyncio

from devtools import debug

from src.framework import Conversation
from src.utils import loggers
from .models import AutoConversationOutput
from ..base import BaseAutomation
from ..scenario import AutoScenario
from .models import AutoConversationConfig


class AutoConversation(BaseAutomation[AutoConversationConfig]):
    async def run_async(self) -> AutoConversationOutput:
        conversation = None

        async with AutoScenario(self.config) as ctx:
            loggers.evaluation.info(
                "Starting automation core. Waiting for 3 seconds..."
            )
            await asyncio.sleep(3)

            for i in range(self.config.message_count):
                loggers.evaluation.info(f"Running iteration {i}")
                user_message = await ctx.user.run_async()
                loggers.evaluation.info(f"User message: {user_message.content}")
                await ctx.client.send_user_message(user_message.content)

                ai_message = await ctx.client.wait_for_ai_message()
                ctx.user.add_message(ai_message)

            messages = [
                m.serializable_copy()
                for m in ctx.scenario.agents[0].full_conversation.messages
            ]
            debug(messages)

            conversation = Conversation(messages=messages)

        return AutoConversationOutput(config=self.config, conversation=conversation)
