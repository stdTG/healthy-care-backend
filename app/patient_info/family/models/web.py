from typing import List, Optional

from pydantic import BaseModel

from core.utils.strings import to_camel


class Family(BaseModel):
    mother: Optional[List[str]]
    father: Optional[List[str]]
    grandmother: Optional[List[str]]
    grandfather: Optional[List[str]]

    class Config:
        alias_generator = to_camel
