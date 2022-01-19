from datetime import date
from typing import Optional

from pydantic import BaseModel

from core.utils.strings import to_camel


class Vaccine(BaseModel):
    name: str
    date: Optional[date]

    class Config:
        alias_generator = to_camel
