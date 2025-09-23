import re
from typing import List, Tuple, Set

from src.framework.models import Message, MessageRole
from ..agents.scenario_agent import ScenarioAgent


def extract_names_from_messages_str(messages_str: str) -> Set[str]:
    # Regular expression to find names (words before a colon)
    pattern = r'\b([A-Za-z]+):'
    found_names = set(re.findall(pattern, messages_str))
    return found_names


def messages_str_to_tuples(conversation: str) -> List[Tuple[str, str]]:
    # Extract names from the conversation
    names = extract_names_from_messages_str(conversation)

    # Escape special characters in names and create a regex pattern
    names_pattern = '|'.join(map(re.escape, names))
    split_pattern = rf'({names_pattern}):([^:]*?(?=(?:{names_pattern}):|$))'

    # Find all occurrences that match the pattern
    matches = re.findall(split_pattern, conversation, re.DOTALL)

    # Create a list of tuples (name, message)
    parsed_conversation = [(match[0], match[1].strip()) for match in matches]

    return parsed_conversation


def str_to_message_list(
        message_str: str,
        agents: List[ScenarioAgent],
        users_name: str,
        users_uid: str,
        scenario_instance_uid: str,
) -> List[Message]:
    parsed_conversation = messages_str_to_tuples(message_str)
    messages: List[Message] = []

    for name, message in parsed_conversation:
        agent = next((agent for agent in agents if agent.name == name), None)
        is_user_message = name == users_name or name in users_name
        if agent is None and not is_user_message:
            raise ValueError(f"Agent with name {name} not found")
        messages.append(Message(
            author_id=users_uid if is_user_message else agent.template.uid,
            author_name=users_name if is_user_message else agent.name,
            role=MessageRole.user if is_user_message else MessageRole.ai,
            content=message,
            scenario_instance_id=scenario_instance_uid,
        ))
    return messages
