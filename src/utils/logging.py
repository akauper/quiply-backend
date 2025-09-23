import inspect
import logging
import sys
from abc import ABC
from typing import TypeVar, Generic

import devtools

from src.settings import quiply_settings, BaseLoggingSettings, AppLoggingSettings

TLoggingSettings = TypeVar('TLoggingSettings', bound=BaseLoggingSettings)


class BaseQuiplyLogger(logging.Logger, ABC, Generic[TLoggingSettings]):
    def __init__(self, name: str, settings: TLoggingSettings = quiply_settings.logging):
        super().__init__(name)
        self.settings: TLoggingSettings = settings

        console_handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        if self.settings.log_to_file:
            file_handler = logging.FileHandler(f'{name}.log')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.addHandler(file_handler)

    def is_debug(self) -> bool:
        return self.isEnabledFor(logging.DEBUG)

    def dev_debug(self, msg, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            # Extract the caller's stack frame
            frame = inspect.currentframe().f_back.f_back
            # Get the caller's file and line number
            filename = frame.f_code.co_filename

            devtools.debug(msg, **kwargs, frame_depth_=3)


class BaseAppLogger(BaseQuiplyLogger[AppLoggingSettings]):
    def __init__(self, name: str, settings: AppLoggingSettings = quiply_settings.logging):
        super().__init__(name, settings)


class GenericAppLogger(BaseAppLogger):
    def __init__(self, settings: AppLoggingSettings = quiply_settings.logging):
        super().__init__('QUIPLY', settings)

        self.setLevel(self.settings.base_log_level.upper())


class SystemLogger(BaseAppLogger):
    def __init__(self):
        super().__init__('QSYSTEM')

        self.setLevel(self.settings.system_log_level.upper())


class FastAPILogger(BaseAppLogger):
    def __init__(self):
        super().__init__('FASTAPI')

        self.setLevel(self.settings.fastapi_log_level.upper())


class StorageLogger(BaseAppLogger):
    def __init__(self):
        super().__init__('STORAGE')

        self.setLevel(self.settings.storage_log_level.upper())


class EvaluationLogger(BaseAppLogger):
    def __init__(self):
        super().__init__('EVALUATION')

        self.setLevel(self.settings.evaluation_log_level.upper())


class FrameworkLogger(BaseAppLogger):
    def __init__(self):
        super().__init__('FRAMEWORK')

        self.setLevel(self.settings.framework_log_level.upper())


class ScenarioLogger(BaseAppLogger):
    def __init__(self):
        super().__init__('SCENARIO')

        self.setLevel(self.settings.scenario_log_level.upper())


TLogger = TypeVar('TLogger', bound=BaseAppLogger)


class QuiplyLoggers:
    def __init__(self):
        self._generic = GenericAppLogger()
        self._system = SystemLogger()
        self._fastapi = FastAPILogger()
        self._storage = StorageLogger()
        self._evaluation = EvaluationLogger()
        self._framework = FrameworkLogger()
        self._scenario = ScenarioLogger()

        self._loggers = {
            self._system.name: self._system,
            self._fastapi.name: self._fastapi,
            self._storage.name: self._storage,
            self._evaluation.name: self._evaluation,
            self._framework.name: self._framework,
            self._scenario.name: self._scenario,
        }

    def get_logger(self, name: str) -> TLogger:
        if name not in self._loggers:
            return self._generic
        return self._loggers[name]

    @property
    def system(self) -> SystemLogger:
        return self._system

    @property
    def fastapi(self) -> FastAPILogger:
        return self._fastapi

    @property
    def storage(self) -> StorageLogger:
        return self._storage

    @property
    def evaluation(self) -> EvaluationLogger:
        return self._evaluation

    @property
    def framework(self) -> FrameworkLogger:
        return self._framework

    @property
    def scenario(self) -> ScenarioLogger:
        return self._scenario


logging.setLoggerClass(BaseQuiplyLogger)
loggers: QuiplyLoggers = QuiplyLoggers()
logger: GenericAppLogger = GenericAppLogger()
