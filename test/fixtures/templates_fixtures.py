from unittest.mock import MagicMock

import pytest
from faker import Faker

from src.models import ScenarioSchema, ActorSchema

from .configs_fixtures import mock_scenario_config

faker = Faker()


@pytest.fixture
def mock_scenario_template(mock_scenario_config):
    mock = MagicMock(spec=ScenarioSchema)

    mock.uid = faker.uuid4()
    mock.name = faker.word()
    mock.description = faker.sentence()
    mock.image_url = faker.url()
    mock.scenario_config = mock_scenario_config

    return mock


@pytest.fixture
def mock_actor_template():
    mock = MagicMock(spec=ActorSchema)

    mock.uid = faker.uuid4()
    mock.name = str(faker.first_name()).lower()
    mock.description = faker.sentence()
    mock.image_url = faker.url()

    return mock
