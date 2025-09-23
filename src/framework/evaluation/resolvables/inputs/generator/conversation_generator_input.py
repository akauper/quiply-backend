from typing import Dict, Any, ClassVar

from pydantic import Field

from src.framework.models import TokenUsage
from src.framework.utils import StopwatchContext
from src.framework.runnables.agents import Agent
from ..base_input import BaseInput
from src.framework.evaluation.results.input_result import InputResult
from src.framework.evaluation.callback import EvaluationCallback
from src.framework.evaluation.context import EvaluationContext


class ConversationGeneratorInput(BaseInput):
    type: ClassVar[str] = "conversation-generator"
    params: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        if "value" not in data:
            data["value"] = "default"
        super().__init__(**data)

    async def resolve_async(self, input: Dict[str, str]) -> InputResult:
        from src.automation import AutoConversationConfig, AutoConversation

        async with StopwatchContext() as sw:
            callback = EvaluationCallback(runnable_type=Agent)
            config = AutoConversationConfig.model_validate(self.params)
            config.agent_callbacks = [callback]

            auto_conversation = AutoConversation(config)
            with EvaluationContext(key=self.value):
                output = await auto_conversation.run_async()

        return InputResult(
            resolvable=self,

            raw_template=self.value,
            vars=input,
            rendered_template='',
            value=output.conversation,

            steps=callback.steps,

            latency_ms=sw.elapsed_ms_int,
            token_usage=TokenUsage() # TODO: Add token_usage
        )
