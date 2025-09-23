import gc
import importlib
import inspect
import os
import sys
from typing import Dict, Callable, List, Literal, get_args, Optional

from starlette.websockets import WebSocket

from src.exceptions import WebsocketScenarioNotFoundException
from src.models import ScenarioInstance, ScenarioResult
from src.utils import logger, loggers
from src.websocket import WebSocketConnection, WebSocketStatus
from src.websocket.error_handler import handle_websocket_exception
from .base import Scenario
from ..settings import quiply_settings

PACKAGE_PATH = os.path.join(os.path.dirname(__file__), 'scenarios')

CallbackType = Callable[[Scenario, Optional[ScenarioResult]], None]

Events = Literal['create', 'start', 'end', 'complete', 'destroy']


class ScenarioManager:
    scenario_classes: Dict[str, type]
    scenarios: Dict[str, Scenario]

    running_scenarios: Dict[str, Scenario]

    callback_dict: Dict[str, List[CallbackType]]

    def __init__(self):
        self.scenario_classes = self._load_scenarios()
        scenario_names = "\n" + "\n".join([f"{idx + 1}: {scenario_id}" for idx, scenario_id in enumerate(list(self.scenario_classes.keys()))])
        loggers.system.info(f'Loaded scenarios: {scenario_names}')
        self.scenarios = {}
        self.running_scenarios = {}

        self.callback_dict = {}
        for event in get_args(Events):
            self.callback_dict[event] = []

    @staticmethod
    def _load_scenarios() -> Dict[str, type]:
        scenario_classes = {}
        root_path = PACKAGE_PATH  # Root path containing scenarios

        for root, dirs, files in os.walk(root_path):
            if 'scenario.py' in files:
                package = os.path.relpath(root, root_path).replace('/', '.')
                module_path = f"{package}.scenario"

                sys.path.insert(0, root_path)
                module = importlib.import_module(module_path)
                sys.path.pop(0)

                for class_name, cls in module.__dict__.items():
                    if isinstance(cls, type) and issubclass(cls, Scenario) and cls is not Scenario:
                        key = package.split('.')[-1].lower()  # Use the package name as the key
                        scenario_classes[key] = cls

        return scenario_classes

    def on(self, event: Events, callback: CallbackType) -> None:
        self.callback_dict[event].append(callback)

    def off(self, event: Events, callback: CallbackType) -> None:
        self.callback_dict[event].remove(callback)

    def _trigger(self, event: Events, scenario: Scenario, result: Optional[ScenarioResult] = None) -> None:
        for callback in self.callback_dict[event]:
            callback(scenario, result)

    def create_scenario(self, scenario_instance: ScenarioInstance, override_settings: dict = None) -> Scenario:
        # self.check_for_lingering_references()

        ScenarioClass = self.scenario_classes.get(scenario_instance.schema_id)
        if ScenarioClass:
            settings = quiply_settings.scenario.model_copy()
            if override_settings:
                settings.update_from(override_settings)

            scenario = ScenarioClass(scenario_instance, settings)
            self.scenarios[scenario_instance.uid] = scenario
            self._trigger('create', scenario)

            loggers.system.info(f'ScenarioManager created scenario with id {scenario_instance.uid} for user {scenario_instance.user_id} from template {scenario_instance.schema_id} with settings {settings}')
            return scenario
        else:
            raise Exception(f'Scenario \'{scenario_instance.schema_id}\' not found')

    async def start_scenario_async(self, websocket: WebSocket, scenario_instance_id: str):
        loggers.system.debug(f'ScenarioManager start_scenario_async scenario with id {scenario_instance_id} for client {websocket.client.host}')

        scenario = self.scenarios.get(scenario_instance_id, None)
        if scenario is None:
            await handle_websocket_exception(websocket, WebsocketScenarioNotFoundException, WebsocketScenarioNotFoundException(stage=WebSocketStatus.GetScenario))

        self.running_scenarios[scenario_instance_id] = scenario

        async with WebSocketConnection(scenario.user_uid, scenario.instance.uid) as connection:
            await connection.connect(scenario, websocket)
            scenario.loggers.websocket.debug(f'WebsocketConnection starting listen loop for client [{scenario.user_uid}] in scenario [{scenario.template_uid}]')
            await connection.listen()

        self._trigger('start', scenario)

    def get_scenario(self, scenario_instance_id: str) -> Scenario | None:
        scenario = self.scenarios.get(scenario_instance_id, None)
        return scenario

    async def end_scenario_async(self, scenario_instance_id: str, completed: bool) -> ScenarioResult | None:
        loggers.system.debug(f'ScenarioManager end_scenario_async scenario with id {scenario_instance_id}')

        if scenario_instance_id in self.scenarios:
            scenario = self.scenarios[scenario_instance_id]
            if completed:
                result = await scenario.lifecycle_manager.end_scenario_async()
                self._trigger('complete', scenario, result)
                # await evaluation_manager.on_scenario_complete_async(scenario, result)
            else:
                result = None
                self._trigger('end', scenario)
                # await evaluation_manager.on_scenario_end_async(scenario)

            self.destroy_scenario(scenario_instance_id)
        else:
            loggers.system.error(f'Cannot call end_scenario_async: No scenario found with id {scenario_instance_id}')
            result = None
        return result

    def destroy_scenario(self, scenario_instance_id: str) -> None:
        scenario = self.scenarios.get(scenario_instance_id)
        if not scenario:
            loggers.system.error(f'Cannot call destroy_scenario: No scenario found with id {scenario_instance_id}')
            return

        self._trigger('destroy', scenario)

        scenario.cleanup()

        del self.running_scenarios[scenario_instance_id]
        del self.scenarios[scenario_instance_id]

        gc.collect()
        # self.check_for_lingering_references()

    @staticmethod
    def check_for_lingering_references():
        # Check for lingering references to the scenario
        for obj in gc.get_objects():
            if isinstance(obj, Scenario):
                try:
                    print(f'Lingering reference to scenario: {obj}')
                    referrers = gc.get_referrers(obj)
                    # objgraph.show_backrefs([obj], filename='backref_graph.png')
                    for ref in referrers:
                        print(f'Referred by: {type(ref)}')
                        if inspect.isclass(ref):
                            print(f'Class name: {ref.__name__}')
                        elif inspect.ismodule(ref):
                            print(f'Module name: {ref.__name__}')
                        elif inspect.isfunction(ref):
                            print(f'Function name: {ref.__name__}')
                        elif inspect.ismethod(ref):
                            print(f'Method name: {ref.__name__}')
                        elif inspect.isframe(ref):
                            print(f'Frame code: {ref.f_code}')
                        elif inspect.istraceback(ref):
                            print(f'Traceback: {ref.tb_frame}')
                except Exception as e:
                    print(f'Error checking for lingering references: {e}')
