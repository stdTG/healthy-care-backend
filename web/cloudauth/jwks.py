from typing import Any, Dict, List

import requests
from pydantic import BaseModel


class JWKS(BaseModel):
    keys: List[Dict[str, Any]]

    @classmethod
    def fromurl(cls, url: str):
        obj = requests.get(url).json()
        return cls.parse_obj(obj)
