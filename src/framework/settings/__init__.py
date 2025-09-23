from pathlib import Path
from typing import Dict, Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings
from .evaluation import EvaluationSettings
from .prompting import PromptingSettings
from .runnables import RunnableSettings

from ..utils import find_project_root

from devtools import debug as _debug


class FrameworkSettings(BaseSettings):
    # If True, settings will be loaded from the root of the project settings.yaml file
    load_from_root_settings: bool = True

    evaluation: EvaluationSettings = Field(default_factory=EvaluationSettings)
    prompting: PromptingSettings = Field(default_factory=PromptingSettings)
    runnables: RunnableSettings = Field(default_factory=RunnableSettings)

    @classmethod
    def _load_root_settings(cls, filename: str = 'settings.yaml') -> Dict[str, Any]:
        settings_dir = find_project_root()
        path = settings_dir / filename

        data: Dict[str, Any] = {}
        if path.exists():
            with open(path, 'r') as file:
                data = yaml.safe_load(file)
        else:
            print(f'Framework Settings file {filename} not found in {settings_dir}')

        return data.get('framework', {})

    @classmethod
    def load(cls, filename: str = 'settings.yaml') -> 'FrameworkSettings':
        settings_dir = Path(__file__).parent.parent
        path = settings_dir / filename

        data: Dict[str, Any] = {}
        if path.exists():
            with open(path, 'r') as file:
                data = yaml.safe_load(file)

            load_root = data.get('load_from_root_settings', False) if data else False
            if load_root:
                data = cls._load_root_settings(filename)
            else:
                data.pop('load_from_root_settings')
        else:
            print(f'Framework Settings file {filename} not found in {settings_dir} - Loading root settings instead')
            data = cls._load_root_settings(filename)

        return cls(**data)


framework_settings = FrameworkSettings.load()
_debug(framework_settings)
