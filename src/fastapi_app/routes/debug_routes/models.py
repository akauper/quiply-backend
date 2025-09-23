from pydantic import BaseModel, ConfigDict


class DebugRespondRequest(BaseModel):
    user_name: str
    message_history: str

    model_config = ConfigDict(
        from_attributes=True,
    )
