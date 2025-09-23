from typing import Optional

from pydantic import BaseModel


class PurgeOptions(BaseModel):
    user_id: Optional[str] = None
    preserve_recent_count: Optional[int] = None
