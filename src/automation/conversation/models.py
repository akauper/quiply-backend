from typing import Optional

from pydantic import Field

from src.framework import Conversation
from ..base import BaseAutomationOutput
from ..scenario.models import AutoScenarioConfig


class AutoConversationConfig(AutoScenarioConfig):
    message_count: int = Field(default=3)


class AutoConversationOutput(BaseAutomationOutput):
    conversation: Optional[Conversation] = Field(default=None)
