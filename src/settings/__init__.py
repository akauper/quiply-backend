from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

import yaml
from pathlib import Path

from .fastapi import FastAPISettings
from .websocket import WebSocketSettings
from .logging import BaseLoggingSettings, AppLoggingSettings
from .services import ServicesSettings, LanguageModelQuality
from .scenario import ScenarioSettings, ScenarioLoggingSettings
from .evaluation import EvaluationSettings
from .debug import DebugSettings

from devtools import debug as _debug


class QuiplySettings(BaseSettings):
    app_title: str = Field(default='Quiply')
    app_version: str = Field(default='1')
    site_domain: str = Field(default='quiply.ai')
    host: str = Field(default='0.0.0.0')
    port: int = Field(default=5005)
    workers: int = Field(default=8)
    reload: bool = Field(default=True)
    timeout: int = Field(default=120)

    fastapi: FastAPISettings = Field(default_factory=FastAPISettings)
    websocket: WebSocketSettings = Field(default_factory=WebSocketSettings)
    logging: AppLoggingSettings = Field(default_factory=AppLoggingSettings)
    services: ServicesSettings = Field(default_factory=ServicesSettings)
    scenario: ScenarioSettings = Field(default_factory=ScenarioSettings)
    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)

    debug: DebugSettings = Field(default_factory=DebugSettings)

    model_config = ConfigDict(
        extra='ignore'
    )

    @classmethod
    def load_settings(cls, settings_filename: str = 'settings.yaml') -> 'QuiplySettings':
        settings_dir = Path(__file__).parent.parent.parent
        settings_path = settings_dir / settings_filename

        settings_data = {}
        if settings_path.exists():
            with open(settings_path, 'r') as file:
                settings_data = yaml.safe_load(file)
        else:
            print(f'Settings file {settings_filename} not found in {settings_dir}')
        return cls(**settings_data)

    def initialize_dependencies(self):
        pass
        # self.services.initialize_dependencies(self.framework)
        # self.scenario.initialize_dependencies(self.services)
        # self.evaluation.initialize_dependencies(self.services)
        # self.framework.initialize_dependencies(self.services, self.scenario, self.evaluation)


quiply_settings = QuiplySettings.load_settings()
_debug(quiply_settings)
# _debug(quiply_settings)
