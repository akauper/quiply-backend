from datetime import datetime

from pydantic import Field, BaseModel

from .models.auto_user_template import AutoUserSchema
from src.framework import (
    TextGenerationRequest,
    ConversationMemory,
    TextGenerator,
    Message,
    TextResponse,
)
from .scenario_instructions import get_scenario_instructions
from ...models import AccountData, SubscriptionType, UserProfile
from ...models.user import UserRole

SYSTEM_MESSAGE_STRUCTURE = """{{instructions}}

### Personality Profile:
Below is a personality profile for the character you are role-playing as. Use this profile to deeply inform your character's behavior, thoughts, and interactions. Your goal is to embody these traits so effectively that the user feels like they are interacting with a real, complex person.
{{personality}}
{% for archetype in archetypes %}
{{archetype}}
{% endfor %}
"""


class AutoUserAgent(BaseModel):
    id: str = Field(default="mock_user_id")
    name: str
    scenario_instance_id: str

    memory: ConversationMemory = Field(default_factory=ConversationMemory)
    text_generator: TextGenerator = Field(default_factory=TextGenerator)

    def set_system_message(self, message: Message) -> None:
        self.memory.add_message(message)

    def add_message(self, message: TextGenerationRequest) -> None:
        self.memory.save(message)

    async def run_async(self) -> Message:
        buffer = self.memory.load()

        text_response: TextResponse = await self.text_generator.run_async(buffer)
        message = Message.from_user(
            content=text_response.content,
            author_id=self.id,
            author_name=self.name,
            scenario_instance_id=self.scenario_instance_id,
        )

        self.add_message(message)
        return message

    @classmethod
    def from_schema(
            cls,
            user_schema: AutoUserSchema,
            scenario_schema_id: str,
            scenario_instance_id: str
    ) -> "AutoUserAgent":
        user = cls(
            name=user_schema.name,
            scenario_instance_id=scenario_instance_id,
        )

        scenario_instructions = get_scenario_instructions(
            scenario_schema_id, user_name=user_schema.name
        )

        import jinja2

        system_message_content = (
            jinja2.Environment()
            .from_string(SYSTEM_MESSAGE_STRUCTURE)
            .render(
                instructions=scenario_instructions,
                personality=user_schema.personality,
                archetypes=user_schema.archetypes,
            )
        )

        user.set_system_message(
            Message.from_system(
                content=system_message_content,
                author_id=user.id,
                author_name=user.name,
                scenario_instance_id=scenario_instance_id,
            )
        )

        return user

    @classmethod
    def from_load_schema(
            cls,
            user_schema_id: str,
            scenario_schema_id: str,
            scenario_instance_id: str
    ) -> "AutoUserAgent":
        template = AutoUserSchema.load(user_schema_id)
        return cls.from_schema(template, scenario_schema_id, scenario_instance_id)

    def to_account_data(self) -> AccountData:
        return AccountData(
            id=self.id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            roles=[UserRole.USER],
            subscription_type=SubscriptionType.UNLIMITED,
            email="debug@quiply.ai",
            first_name=self.name,
            last_name="Autonomous",
            profile=UserProfile(
                account_id=self.id,
                name=self.name,
            ),
        )
