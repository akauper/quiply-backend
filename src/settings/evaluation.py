from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings


class EvaluationMode(str, Enum):
    replace_prompts = "replace_prompts"  # Replace prompts with the provided prompt key
    multi_prompt = "multi_prompt"  # Run all prompts evaluation_count times using provided evaluation key


class EvaluationSettings(BaseSettings):
    enabled: bool = Field(default=False)
    mode: EvaluationMode = Field(default=EvaluationMode.replace_prompts)

    evaluation_count: int = Field(default=1)
    evaluation_prompt_key: str = Field(default="default")

    @property
    def multi_eval_enabled(self) -> bool:
        return self.enabled and self.mode == EvaluationMode.multi_prompt
