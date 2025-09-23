from enum import Enum


class AgentType(str, Enum):
    AGENT = 'agent'
    SPECIAL_AGENT = 'special_agent'
    MENTOR = 'mentor'
