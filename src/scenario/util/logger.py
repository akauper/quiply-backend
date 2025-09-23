from typing import TypeVar

from src.settings import ScenarioLoggingSettings
from src.utils.logging import BaseQuiplyLogger


class BaseScenarioLogger(BaseQuiplyLogger[ScenarioLoggingSettings]):
    def __init__(self, name: str, settings: ScenarioLoggingSettings):
        super().__init__(name, settings)


class GenericScenarioLogger(BaseScenarioLogger):
    def __init__(self, settings: ScenarioLoggingSettings):
        super().__init__('SCENARIO', settings)

        self.setLevel(settings.base_log_level.upper())


class StageLogger(BaseScenarioLogger):
    def __init__(self, settings: ScenarioLoggingSettings):
        super().__init__('STAGE', settings)

        self.setLevel(settings.stage_log_level.upper())


class LLMLogger(BaseScenarioLogger):
    def __init__(self, settings: ScenarioLoggingSettings):
        super().__init__('LLM', settings)

        self.setLevel(settings.llm_log_level.upper())


class WebsocketLogger(BaseScenarioLogger):
    def __init__(self, settings: ScenarioLoggingSettings):
        super().__init__('WEBSOCKET', settings)

        self.setLevel(settings.websocket_log_level.upper())


TScenarioLogger = TypeVar('TScenarioLogger', bound=BaseScenarioLogger)


class ScenarioLoggers:
    def __init__(self, settings: ScenarioLoggingSettings):
        self._generic = GenericScenarioLogger(settings)
        self._stage = StageLogger(settings)
        self._llm = LLMLogger(settings)
        self._websocket = WebsocketLogger(settings)

        self._loggers = {
            self._generic.name: self._generic,
            self._stage.name: self._stage,
            self._llm.name: self._llm,
            self._websocket.name: self._websocket,
        }

    def get_logger(self, name: str) -> TScenarioLogger:
        if name not in self._loggers:
            return self._generic
        return self._loggers[name]

    @property
    def stage(self) -> StageLogger:
        return self._stage

    @property
    def llm(self) -> LLMLogger:
        return self._llm

    @property
    def websocket(self) -> WebsocketLogger:
        return self._websocket
