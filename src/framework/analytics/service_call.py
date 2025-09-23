from typing import Optional, Any
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, ConfigDict

from src.utils import get_data_path_str, loggers


class ServiceCall(BaseModel):
    service_name: str
    service_type: str

    start_timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    end_timestamp: Optional[float] = Field(default=None)
    cost: Optional[float] = Field(default=None)

    model_config = ConfigDict(extra='allow')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

    def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end()

    @property
    def timedelta(self) -> timedelta:
        if self.end_timestamp is None:
            return timedelta.min
        return datetime.fromtimestamp(self.end_timestamp) - datetime.fromtimestamp(self.start_timestamp)

    @property
    def duration(self) -> float:
        if not self.end_timestamp:
            return -1
        return self.timedelta.total_seconds()

    def end(
            self,
            *,
            log: Optional[bool] = True,
            save: Optional[bool] = True,
            **kwargs: Any
    ):
        self.end_timestamp = datetime.now().timestamp()

        for k, v in kwargs.items():
            self.__setattr__(k, v)

        if log:
            self.log()
        if save:
            self.save()

    def save(self):
        try:
            path = get_data_path_str() + '/analytics/service_calls'
            path += f'/{self.service_name}_{datetime.fromtimestamp(self.start_timestamp).strftime("%Y-%m-%d_%H-%M-%S")}.json'
            json = self.model_dump_json(indent=4)
            with open(path, 'w') as f:
                f.write(json)
        except Exception as e:
            loggers.framework.error(f'Error saving service call: {e}')

    def log(self):
        loggers.framework.info(f'Service Call: {self.service_name} - {self.service_type} - {self.duration} - {self.cost}')

