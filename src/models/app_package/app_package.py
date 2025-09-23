import json
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from ..schemas import ActorSchema, LobbyTreeSchema, ScenarioSchema
from src.utils import logger, get_project_path_str

APP_PACKAGE_PATH = 'data/app_package.json'


class AppPackageData(BaseModel):
    version: int

    image_paths: Dict[str, str] = Field(default_factory=dict)

    lobby_tree: Optional[LobbyTreeSchema] = None

    actors: List[ActorSchema] = Field(default_factory=list)
    scenarios: List[ScenarioSchema] = Field(default_factory=list)


class AppPackage:
    _data: AppPackageData | None

    @property
    def valid(self) -> bool:
        return self._data is not None

    @property
    def version(self) -> int:
        return self._data.version

    @property
    def data(self) -> AppPackageData:
        return self._data

    @property
    def lobby_tree(self) -> Optional[LobbyTreeSchema]:
        return self._data.lobby_tree

    @property
    def actors(self) -> List[ActorSchema]:
        return self._data.actors

    @property
    def scenarios(self) -> List[ScenarioSchema]:
        return self._data.scenarios

    def __init__(self, data: AppPackageData | None):
        self._data = data

    @classmethod
    def from_local(cls) -> 'AppPackage':
        try:
            with open(APP_PACKAGE_PATH, 'r', encoding='utf-8') as file:
                data_dict: dict = json.load(file)
                data = AppPackageData.model_validate(data_dict)
                return cls(data)
        except FileNotFoundError:
            logger.warning(f"App package not found at {APP_PACKAGE_PATH}.")

    def save(self) -> None:
        if self._data is None:
            raise Exception("App package data not loaded.")
        try:
            file_name = get_project_path_str() + "/" + APP_PACKAGE_PATH
            with open(file_name, 'w', encoding='utf-8') as file:
                package_dict = self._data.model_dump()
                json.dump(package_dict, file, ensure_ascii=False, indent=4)
        except FileNotFoundError as e:
            logger.error(f"Error saving app package: {e}")
            raise e

    def check_data(self) -> bool:
        if self._data is None:
            logger.fatal("App package data not loaded.")
            return False
        return True

    def get_actor(self, uid: str) -> ActorSchema | None:
        if not self.check_data():
            return None
        return next((actor for actor in self._data.actors if actor.uid == uid), None)

    def update_actors(self, actors: List[ActorSchema]) -> None:
        if not self.check_data():
            return
        self._data.actors = actors
        self.save()

    def get_scenario(self, uid: str) -> ScenarioSchema | None:
        if not self.check_data():
            return None
        return next((scenario for scenario in self._data.scenarios if scenario.uid == uid), None)

    def update_scenarios(self, scenarios: List[ScenarioSchema]) -> None:
        if not self.check_data():
            return
        self._data.scenarios = scenarios
        self.save()