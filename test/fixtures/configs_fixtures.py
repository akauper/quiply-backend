from unittest.mock import MagicMock

import pytest

from src.models import ScenarioConfig
from faker import Faker

fake = Faker()


@pytest.fixture
def mock_scenario_config():
    mock = MagicMock(spec=ScenarioConfig)

    mock.schema_id = "test_scenario_template_id"
    mock.name = "test_scenario_config_name"
    mock.user_id = "test_scenario_user_id"

    mock.actor_ids = ["test_scenario_actor_id_1", "test_scenario_actor_id_2"]

    return mock