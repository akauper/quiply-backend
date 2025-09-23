from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class ActorToolkitSchema(BaseModel):
    temperature: Optional[float] = 0.7
    has_tools: Optional[bool] = False
    tool_names: Optional[List[str]] = Field(default_factory=list)
    tool_kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)
