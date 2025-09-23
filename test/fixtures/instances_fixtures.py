from unittest.mock import MagicMock

import pytest

from src.models import ScenarioInstance

from .base_fixtures import mock_quiply_user
from .configs_fixtures import mock_scenario_config

from faker import Faker

fake = Faker()


@pytest.fixture
def mock_scenario_instance(mock_scenario_config, mock_quiply_user):
    mock = MagicMock(spec=ScenarioInstance)

    mock.uid = fake.uuid4()
    mock.scenario_config = mock_scenario_config
    mock.quiply_user = mock_quiply_user

    return mock
