from enum import Enum


class WebsocketStage(str, Enum):
    GetScenario = 'get_scenario'
    AcceptConnection = 'accept_connection'
    WaitForReadyEvent = 'wait_for_ready_event'
    SendReadyEvent = 'send_ready_event'
    InitializeScenario = 'initialize_scenario'
    ScenarioRunning = 'scenario_running'
