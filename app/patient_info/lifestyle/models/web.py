from typing import Optional

from pydantic import BaseModel

from core.utils.strings import to_camel


class Lifestyle(BaseModel):
    activity: str
    description: Optional[str]

    class Config:
        alias_generator = to_camel
