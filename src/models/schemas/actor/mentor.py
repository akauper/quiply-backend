from typing import Literal

from ..schema import Schema


class MentorSchema(Schema):
    type: Literal['advisor'] = 'advisor'

