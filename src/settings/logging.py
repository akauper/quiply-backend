from pydantic import Field
from pydantic_settings import BaseSettings


class BaseLoggingSettings(BaseSettings):
    base_log_level: str = 'INFO'
    log_to_file: bool = False


class AppLoggingSettings(BaseLoggingSettings):
    system_log_level: str = 'INFO'
    fastapi_log_level: str = 'INFO'
    storage_log_level: str = 'INFO'
    evaluation_log_level: str = 'INFO'
    framework_log_level: str = 'INFO'
    scenario_log_level: str = 'INFO'
