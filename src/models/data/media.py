from typing import Optional

from pydantic import Field


class LocalImageMixin:
    local_image_path: Optional[str] = Field(default=None)
    """ A local path to a unique image. This image needs to be uploaded. """

    local_image_link: Optional[str] = Field(default=None)
    """ A link to a local path of an image that has already been uploaded. """

    image_url: Optional[str] = Field(default=None)
    """ The remote URL of the image. """


class LocalVideoMixin:
    local_video_path: Optional[str] = Field(default=None)
    """ The local path to the video. """

    video_url: Optional[str] = Field(default=None)
    """ The remote URL of the video. """
