from typing import Optional, List, TypeVar

from pydantic import Field, BaseModel, ConfigDict, model_validator

from .page_schema import PageSchema
from ..schema import Schema
from ..actor import ActorSchema, ActorToolkitSchema
from ...data.media import LocalImageMixin


class ActorSettingsSchema(BaseModel):
    min_actor_count: int = 1
    """ The minimum number of actors required for the scenario. """

    max_actor_count: int = 1
    """ The maximum number of actors allowed for the scenario. """

    default_actor_count: int = 1
    """ The default number of actors to use for the scenario. """

    default_actor_ids: Optional[List[str]] = None
    """ The default actor IDs to use for the scenario. """

    default_actor_toolkit: Optional[ActorToolkitSchema] = Field(default_factory=ActorToolkitSchema)
    """ The default toolkit to use for the actors. """

    actor_title: str = 'Actor'
    """ The title to display for the actors. """

    actor_traits: Optional[List[str]] = Field(default_factory=list, validate_default=True)
    """ The traits to display for the actors. """

    summarize_actor_personalities: Optional[bool] = False
    """ Whether to summarize the personalities of the actors. """

    def get_actor_components(self, actor_template: ActorSchema):
        return actor_template.get_components_that_include_fields(self.actor_traits)


class ScenarioSchema(Schema, LocalImageMixin):
    type: str = 'scenario'

    banner_image_url: Optional[str] = None
    """ The URL of the banner image to display. """

    video_idle_url: Optional[str] = None
    """ The URL of the video to display when the scenario is idle. """

    default_theme: Optional[str] = None
    """ The default theme to use for the scenario. """

    pages: List[PageSchema] = Field(default_factory=list)
    """ A list of pages to display when configuring the scenario. """

    actor_settings: ActorSettingsSchema = Field(default_factory=ActorSettingsSchema)
    """ The configuration for the actors in the scenario. """

    model_config = ConfigDict(
        from_attributes=True,
        extra='allow'
    )

    # @model_validator(mode='after')
    # def set_scenario_template_id(self) -> 'ScenarioTemplate':
    #     for field in self.fields:
    #         field.scenario_template_id = self.uid
    #     return self
