from typing import Dict
from uuid import uuid4

from src.models import ScenarioInstance, ScenarioConfig
from src.scenario import scenario_manager, Scenario
from .auto_user_agent import AutoUserAgent
from .models import AutoScenarioConfig
from .websocket_client import AutoScenarioWebSocketClient
from ..base import BaseAutomation


class AutoScenario(BaseAutomation[AutoScenarioConfig]):
    def __init__(self, config: AutoScenarioConfig):
        super().__init__(config)

        scenario_instance_id = str(uuid4())

        self.user = AutoUserAgent.from_load_schema(
            config.auto_user_schema_id, config.scenario_schema_id,scenario_instance_id
        )

        self.instance = ScenarioInstance(
            uuid=scenario_instance_id,
            account_data=self.user.to_account_data(),
            scenario_config=ScenarioConfig(
                schema_id=config.scenario_schema_id,
                name=config.scenario_name,
                user_id=self.user.id,
                field_values=config.field_values,
                difficulty=config.difficulty,
                duration=config.duration,
                actor_ids=config.actor_ids,
            ),
        )

        self.scenario: Scenario | None = None
        self.client: AutoScenarioWebSocketClient | None = None

    async def run_async(self) -> "AutoScenario":
        override_settings: Dict[str, str] = {
            "message_mode": "async",
            "agent_callbacks": self.config.agent_callbacks,
        }
        self.scenario = scenario_manager.create_scenario(
            self.instance, override_settings
        )

        self.client = AutoScenarioWebSocketClient(
            self.user.id, self.instance.uid
        )
        await self.client.connect()
        return self

    async def close(self) -> None:
        await self.client.close()

    async def __aenter__(self) -> "AutoScenario":
        return await self.run_async()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False
