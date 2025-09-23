import pytest

from src.framework import Prompt


@pytest.fixture
def prompt():
    return Prompt(template="Hello {name}")


@pytest.fixture
def evaluable_prompt():
    return Prompt(template="Hello {name}")


def test_prompt_format(prompt):
    assert prompt.format(name="World") == "Hello World"
    print(prompt.input_keys)
    # assert 'World' in prompt.input_keys
