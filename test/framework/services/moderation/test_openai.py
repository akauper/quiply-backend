import pytest
import time

from devtools import debug

from src.framework.runnables.generators.models import ModerationResponse
from src.framework.runnables.generators.moderation.services.get import get_moderation_service


@pytest.fixture
def violation_message():
    return 'Your a stupid jew. I want to have sex with you.'


@pytest.mark.asyncio
class TestModerationOpenAi:
    async def test_run_async(self, violation_message):
        start_time = time.time()

        service = get_moderation_service('openai')
        assert service is not None

        response: ModerationResponse = await service.run_async(violation_message)

        debug(response)
        assert response is not None

        print(f'OpenAI test_run_async took {time.time() - start_time} seconds')