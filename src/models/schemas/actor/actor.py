from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict

from ..schema import Schema
from ...data.media import LocalImageMixin


class ActorComponent(ABC, BaseModel):
    def format(self) -> str:
        traits = []
        for field_name in self.__annotations__.keys():
            field_value = getattr(self, field_name)
            if field_value:
                if isinstance(field_value, list):
                    traits.append(self.format_list_field(field_name, field_value))
                else:
                    traits.append(self.format_field(field_name, field_value))
        formatted_traits = "\t" + self.get_separator().join(traits)
        return f"""{self.get_header()}
{formatted_traits}"""

    @abstractmethod
    def get_header(self):
        pass

    def format_field(self, field_name: str, field_value: str) -> str:
        return f"{field_name.capitalize()}: {field_value}"

    def format_list_field(self, field_name: str, field_value: List[str]):
        processed_values = [item if item.endswith('.') else f"{item}." for item in field_value]
        joined_values = ' '.join(processed_values)
        return f"{field_name.capitalize()}: {joined_values}"

    def get_separator(self):
        return '\n\t'

    def has_attr(self, attr: str) -> bool:
        return hasattr(self, attr) and getattr(self, attr) is not None


TActorComponent = TypeVar('TActorComponent', bound=ActorComponent)


class Behaviours(ActorComponent):
    professional: Optional[str] = None
    negotiation: Optional[str] = None
    social: Optional[str] = None
    relational: Optional[str] = None
    diplomatic: Optional[str] = None
    strategic: Optional[str] = None
    dominance: Optional[str] = None
    adversarial: Optional[str] = None
    confrontational: Optional[str] = None
    supportive: Optional[str] = None

    def get_header(self):
        return "Your primary behaviour:"


class Identity(ActorComponent):
    age: Optional[str] = None
    gender: Optional[str] = None
    sexual: Optional[str] = None
    ethnicity: Optional[str] = None

    def get_header(self):
        return "Identity:"


class Traits(ActorComponent):
    intellect: List[str] = Field(default_factory=list[str])
    emotion: List[str] = Field(default_factory=list[str])
    charisma: List[str] = Field(default_factory=list[str])
    attitude: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Facts about the character you are role-playing:"


class Communication(ActorComponent):
    vocab: Optional[str] = None
    tone: Optional[str] = None
    profanity: Optional[str] = None
    dialect: Optional[str] = None
    lingo: Optional[str] = None
    jargon: Optional[str] = None

    def get_header(self):
        return "Use the following communication style:"

    def format_field(self, field_name: str, field_value: str) -> str:
        return f"{field_value} {field_name}"

    def get_separator(self):
        return ', '


class Preferences(ActorComponent):
    loves: List[str] = Field(default_factory=list[str])
    hates: List[str] = Field(default_factory=list[str])
    listening_preferences: List[str] = Field(default_factory=list[str])
    reading_preferences: List[str] = Field(default_factory=list[str])
    watching_preferences: List[str] = Field(default_factory=list[str])
    activity_preferences: List[str] = Field(default_factory=list[str])
    culinary_preferences: List[str] = Field(default_factory=list[str])
    travel_preferences: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Preferences:"


class Socioeconomic(ActorComponent):
    education: Optional[str] = None
    career: Optional[str] = None
    financial: Optional[str] = None
    home: Optional[str] = None

    def get_header(self):
        return "Socioeconomic:"


class Ideology(ActorComponent):
    religion: Optional[str] = None
    alignment: Optional[str] = None
    outlook: Optional[str] = None
    party: Optional[str] = None

    def get_header(self):
        return "Ideology:"


class Expression(ActorComponent):
    verbal_mannerisms: List[str] = Field(default_factory=list[str])
    humor: List[str] = Field(default_factory=list[str])
    topics: List[str] = Field(default_factory=list[str])
    pet_peeves: List[str] = Field(default_factory=list[str])
    triggers: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Expression:"


class Values(ActorComponent):
    beliefs: List[str] = Field(default_factory=list[str])
    principles: List[str] = Field(default_factory=list[str])
    influences: List[str] = Field(default_factory=list[str])
    dilemmas: List[str] = Field(default_factory=list[str])
    motivations: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Values:"


class Background(ActorComponent):
    hometown: Optional[str] = None
    heritage: Optional[str] = None
    nationality: Optional[str] = None
    history: List[str] = Field(default_factory=list[str])
    experiences: List[str] = Field(default_factory=list[str])
    roots: List[str] = Field(default_factory=list[str])
    challenges: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "History:"


class Memories(ActorComponent):
    fond_memories: List[str] = Field(default_factory=list[str])
    traumatic_memories: List[str] = Field(default_factory=list[str])
    failures: List[str] = Field(default_factory=list[str])
    achievements: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Memories:"


class Goals(ActorComponent):
    short_term_goals: List[str] = Field(default_factory=list[str])
    long_term_goals: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Goals:"


class Skills(ActorComponent):
    formal_skills: List[str] = Field(default_factory=list[str])
    informal_skills: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Skills:"


class Relationships(ActorComponent):
    family: List[str] = Field(default_factory=list[str])
    acquaintances: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Relationships:"


class Routine(ActorComponent):
    weekday_routine: List[str] = Field(default_factory=list[str])
    weekend_routine: List[str] = Field(default_factory=list[str])
    breaking_routine: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Daily Life:"


class Internal(ActorComponent):
    secrets: List[str] = Field(default_factory=list[str])
    fears: List[str] = Field(default_factory=list[str])
    dreams: List[str] = Field(default_factory=list[str])
    regrets: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Internal:"


class Physical(ActorComponent):
    appearance: List[str] = Field(default_factory=list[str])
    fashion: List[str] = Field(default_factory=list[str])
    health: List[str] = Field(default_factory=list[str])

    def get_header(self):
        return "Physical:"


class Image(ActorComponent):
    color_palette: List[str] = Field(default_factory=list[str])
    image_description: Optional[str] = None
    image_prompt: Optional[str] = None

    def get_header(self):
        return "Image:"


class ActorSchema(Schema, LocalImageMixin):
    type: Literal['actor'] = 'actor'
    selected_voice_id: Optional[str] = Field(default='')

    video_idle_url: Optional[str] = Field(default=None)
    video_intro_url: Optional[str] = Field(default=None)

    # Overview
    qualities: List[str] = Field(default_factory=list[str])
    essence: Optional[str] = Field(default='')
    profile: Optional[str] = Field(default='')
    autobiography: Optional[str] = Field(default='')

    # Components
    behaviours: Behaviours = Field(default_factory=Behaviours)
    identity: Identity = Field(default_factory=Identity)
    traits: Traits = Field(default_factory=Traits)
    communication: Communication = Field(default_factory=Communication)
    preferences: Preferences = Field(default_factory=Preferences)
    socioeconomic: Socioeconomic = Field(default_factory=Socioeconomic)
    ideology: Ideology = Field(default_factory=Ideology)
    expression: Expression = Field(default_factory=Expression)
    values: Values = Field(default_factory=Values)
    background: Background = Field(default_factory=Background)
    memories: Memories = Field(default_factory=Memories)
    goals: Goals = Field(default_factory=Goals)
    skills: Skills = Field(default_factory=Skills)
    relationships: Relationships = Field(default_factory=Relationships)
    routine: Routine = Field(default_factory=Routine)
    internal: Internal = Field(default_factory=Internal)
    physical: Physical = Field(default_factory=Physical)
    image: Image = Field(default_factory=Image)

    # @classmethod
    # def get_components_that_include_fields(cls, fields: List[str]) -> List[TActorComponent]:
    #     components: List[tuple[str, TActorComponent]] = [(field_name, getattr(cls, field_name)) for field_name in cls.__annotations__.keys() if isinstance(getattr(cls, field_name), ActorComponent)]
    #     listed_components: List[TActorComponent] = [tup[1] for tup in components if any([tup[0] == field for field in fields])]
    #
    #
    #     return [getattr(cls, field_name) for field_name in cls.__annotations__.keys() if
    #             isinstance(getattr(cls, field_name), ActorComponent) and any([getattr(cls, field_name).has_attr(field) for field in fields])]

    def get_components_that_include_fields(self, fields: List[str]) -> List[TActorComponent]:
        if fields is None or len(fields) == 0:
            return []
        components: List[TActorComponent] = []
        unique_component_ids = set()

        # Iterate through the model fields
        for field_name, model_field in self.model_fields.items():
            component = getattr(self, field_name, None)
            if component is not None and isinstance(component, ActorComponent):
                # Check if the field name is in the fields list or any attribute of the component matches the fields
                if field_name in fields or any(field in fields for field in dir(component)):
                    # We use the id of the component to maintain uniqueness
                    if id(component) not in unique_component_ids:
                        unique_component_ids.add(id(component))
                        components.append(component)

        return components

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow',
    )

