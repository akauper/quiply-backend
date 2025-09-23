from pydantic import BaseModel


class ScenarioDifficulty(BaseModel):
    name: str
    description: str


class ScenarioDuration(BaseModel):
    name: str
    description: str
