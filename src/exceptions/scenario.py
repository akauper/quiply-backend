from abc import ABC

from .base import BaseQuiplyException


class BaseScenarioException(BaseQuiplyException, ABC):
    """Base class for exceptions in this module."""

    stage_name: str

    def __init__(self, stage_name: str, *args):
        self.stage_name = stage_name
        super().__init__(stage_name, *args)


class ScenarioAwakeException(BaseScenarioException):
    """Raised when there is an error during the awake of the scenario"""
    def __init__(self, *args):
        super().__init__('awake', *args)


class ScenarioStartException(BaseScenarioException):
    """Raised when there is an error during the start of the scenario"""

    def __init__(self, *args):
        super().__init__('start', *args)


class ScenarioStepException(BaseScenarioException):
    """Raised when there is an error during the step of the scenario"""
    def __init__(self, *args):
        super().__init__('step', *args)


class ScenarioLateStepException(BaseScenarioException):
    """Raised when there is an error during the step of the scenario"""
    def __init__(self, *args):
        super().__init__('late_step', *args)


class ScenarioUpdateException(BaseScenarioException):
    """Raised when there is an error during the update of the scenario"""
    def __init__(self, *args):
        super().__init__('update', *args)
