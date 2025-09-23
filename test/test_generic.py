from pathlib import Path
from typing import List

import pytest
from devtools import debug

from dotenv import load_dotenv

from src.framework import Runnable, RunnableParams, BaseAsyncCallback, Agent

load_dotenv()


class SomeCallback(BaseAsyncCallback):
    pass


def test1():
    callbacks: List[BaseAsyncCallback] = [SomeCallback()]
    runnable_params = RunnableParams()
    agent = Agent(service_name='abc', runnable_params=runnable_params, temperature=0.112, callbacks=callbacks, verbose=True, something_unused='unused', voice_id='sad', force_long_context = True)

    debug(agent)

