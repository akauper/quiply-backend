from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EvaluationSettings(BaseSettings):
    enabled: bool = Field(default=False)

    evaluation_prompt_key: str = Field(default='default')
    prompt_keys: List[str] = Field(default_factory=list)
    included_runnable_types: List[str] = Field(default_factory=list)
    multi_run_count: int = Field(default=1)

    # model_config = SettingsConfigDict(env_prefix='EVALUATION_', env_file='.env')
