import asyncio
from abc import ABC
from typing import TYPE_CHECKING, TypeVar, Coroutine, Union

from src.models import ScenarioInstance, ScenarioSchema, ScenarioConfig, AccountData
from .scenario_state_base import ScenarioStateObject
from ..models.base_scenario_params import BaseScenarioParams
from ..util import GenericScenarioLogger, ScenarioLoggers

if TYPE_CHECKING:
    from src.websocket import WebSocketConnection

T = TypeVar("T", bound="ScenarioComponent")
TScenario = TypeVar("TScenario", bound="Scenario")


class ScenarioComponent(ScenarioStateObject, ABC):
    scenario: TScenario
    priority: int  # Lower priority is called first

    def __init__(
        self,
        scenario: TScenario,
        priority: int = 100,
    ) -> None:
        self.scenario = scenario
        self.priority = priority

    def cleanup(self):
        del self.scenario

    # region Helper Methods
    def create_task(self, coroutine: Union[Coroutine, list[Coroutine]]) -> asyncio.Task:
        return self.scenario.create_task(coroutine)

    def defer_coroutine(self, coroutine: Union[Coroutine, list[Coroutine]]):
        self.scenario.defer_coroutine(coroutine)

    # endregion

    # region Properties
    @property
    def logger(self) -> GenericScenarioLogger:
        return self.scenario.logger

    @property
    def loggers(self) -> ScenarioLoggers:
        return self.scenario.loggers

    @property
    def scenario_instance(self) -> ScenarioInstance:
        return self.scenario.instance

    @property
    def scenario_template(self) -> ScenarioSchema:
        return self.scenario.template

    @property
    def template_uid(self) -> str:
        return self.scenario.template_uid

    @property
    def instance_uid(self) -> str:
        return self.scenario.instance_uid

    @property
    def scenario_config(self) -> ScenarioConfig:
        return self.scenario.instance.scenario_config

    @property
    def settings(self) -> BaseScenarioParams:
        return self.scenario.params

    @property
    def account_data(self) -> AccountData:
        return self.scenario.instance.account_data

    @property
    def scenario_name(self) -> str:
        return self.scenario.scenario_name

    @property
    def user_uid(self) -> str:
        return self.scenario.user_uid

    @property
    def users_name(self) -> str:
        return self.scenario.users_name

    @property
    def users_prefix(self) -> str:
        return self.scenario.users_prefix

    @property
    def websocket_connection(self) -> "WebSocketConnection":
        return self.scenario.websocket_connection

    # endregion
