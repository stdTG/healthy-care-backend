from typing import Optional

from pydantic import BaseModel

from core.utils.strings import to_camel
from web.core import ObjectIdStr


class DbHost(BaseModel):
    id: Optional[ObjectIdStr] = None

    alias: str
    name: str
    description: str
    connection_string_format: Optional[str]
    db_host: str
    db_user: Optional[str]
    db_password: Optional[str]

    class Config:
        alias_generator = to_camel
