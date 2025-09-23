from typing import Optional, List, Union, Dict

from pydantic import BaseModel, Field

from ...data.media import LocalImageMixin


class LobbyTileSchema(BaseModel, LocalImageMixin):
    id: str
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    locked: Optional[bool] = False
    scenario_link_id: Optional[str] = None  # Settings this flags to start a scenario


class LobbyPageSchema(BaseModel):
    id: str
    title: str
    tiles: List[LobbyTileSchema] = Field(default_factory=list)


class LobbyTreeSchema(BaseModel):
    root: LobbyPageSchema
    pages: Dict[str, LobbyPageSchema] = Field(default_factory=dict)
