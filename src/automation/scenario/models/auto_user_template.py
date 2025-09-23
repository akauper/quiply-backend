import json
from typing import List

from pydantic import BaseModel, Field

from src.utils import get_data_path

import yaml


class AutoUserSchema(BaseModel):
    name: str
    personality: str
    archetypes: List[str] = Field(default_factory=list)

    @classmethod
    def load(cls, schema_id: str) -> 'AutoUserSchema':
        path = get_data_path() / 'automation' / 'auto_user_templates.yaml'
        try:
            with open(path, 'r') as f:
                yaml_data = yaml.safe_load(f)
            data = yaml_data[schema_id]
            return cls.model_validate(data)
        except Exception as e:
            raise e
