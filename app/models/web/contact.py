from pydantic import BaseModel

from core.utils.strings import to_camel


class Contact(BaseModel):
    type: str
    value: str

    class Config:
        alias_generator = to_camel
