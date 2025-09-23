import json
import re
from datetime import datetime
from typing import Optional, TypeVar, List
from uuid import uuid4

from pydantic import BaseModel, Field, ValidationError

from src.models.subscription.subscription_type import SubscriptionType, Subscribable
from src.utils import create_uuid

T = TypeVar("T", bound=BaseModel)

PYDANTIC_FORMAT_INSTRUCTIONS = """The output should be formatted as a RFC8259 compliant JSON instance that conforms to the JSON schema below.

As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Do not include the schema in the output. Only include the data.

Here is the output schema:
```
{schema}
```"""


class ParseableModel(BaseModel):
    @classmethod
    def parse(cls, text: str) -> T:
        try:
            # Greedy search for 1st json candidate.
            match = re.search(
                r"\{.*\}", text.strip(), re.MULTILINE | re.IGNORECASE | re.DOTALL
            )
            json_str = ""
            if match:
                json_str = match.group()
            json_object = json.loads(json_str, strict=False)
            return cls.model_validate(json_object)
        except (json.JSONDecodeError, ValidationError) as e:
            name = cls.__name__
            msg = f"Failed to parse {name} from completion {text}. Got: {e}"
            raise Exception(msg + text)
        except Exception as e:
            name = cls.__name__
            msg = f"Failed to parse {name} from completion {text}. Got: {e}"
            raise Exception(msg + text)

    @classmethod
    def get_format_instructions(cls) -> str:
        schema = cls.model_json_schema()

        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # if "additionalProperties" in reduced_schema:
        #     del reduced_schema["additionalProperties"]

        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema)

        return PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)


class UIDObject(ParseableModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))

    @classmethod
    def create(cls, seed: str = None):
        return create_uuid(seed)


class TimestampObject(BaseModel):
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())

    def update_timestamp(self):
        self.updated_at = datetime.now().isoformat()


class SerializableObject(UIDObject, TimestampObject):
    pass


class Tileable(SerializableObject, Subscribable):
    type: str = Field(default='tileable')
    name: str
    description: str = Field(default='')
    image_url: str = Field(default='')
