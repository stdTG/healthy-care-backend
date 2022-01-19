from pydantic import BaseModel, Field
from typing import List


class AuthClaims(BaseModel):
    sub: str = Field("")
    username: str = Field("")
    email: str = Field("")
    roles: List[str] = Field("")
