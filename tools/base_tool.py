from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseTool(BaseModel, ABC):
    @abstractmethod
    def run_all(self, **kwargs) -> None:
        pass
