import pytest
from pydantic import ConfigDict

from src.framework.models import MessageRole
from src.scenario.agents.scenario_agent import ScenarioAgent


@pytest.fixture
def scenario_agent(mock_scenario, mock_actor_template) -> ScenarioAgent:
    from src.scenario import Scenario
    from src.models import ActorSchema

    agent = ScenarioAgent(
        scenario=mock_scenario,
        template=mock_actor_template,
    )

    return agent


class TestScenarioAgent:
    @pytest.mark.asyncio
    async def test_scenario_agent_run_async(self, memory_messages, scenario_agent):
        scenario_agent.add_message(memory_messages)
        response_message = await scenario_agent.run_async('What is my name?')
        print(response_message)
        assert response_message.is_from(MessageRole.ai)
