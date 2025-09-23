from abc import ABC, abstractmethod
from typing import TypeVar, Any, Generic

from pydantic import BaseModel, Field

from src.framework import CreatedAtMixin, UIDMixin
from src.utils import get_data_path


class BaseAutomationConfig(BaseModel):
    pass


TConfig = TypeVar('TConfig', bound=BaseAutomationConfig)


class BaseAutomationOutput(UIDMixin, CreatedAtMixin):
    config: TConfig = Field(default_factory=BaseAutomationConfig)

    def save(self) -> str:
        path = get_data_path() / "evaluation" / "data" / f"{self.id}.json"
        # Ensure path exists, if not create
        path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure file exists, if not create
        path.touch(exist_ok=True)
        json = self.model_dump_json(indent=4)
        with open(path, 'w') as f:
            f.write(json)
        print(f"Saved Automation Output to {path}")
        return str(path)


TOutput = TypeVar('TOutput', bound=BaseAutomationOutput)


class BaseAutomation(ABC, Generic[TConfig]):

    def __init__(self, config: TConfig):
        self.config = config

    @abstractmethod
    async def run_async(self, *args, **kwargs) -> TOutput | Any:
        pass
