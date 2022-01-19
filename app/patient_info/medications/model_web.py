from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.utils.strings import to_camel


class Medication(BaseModel):
    id: Optional[str] = None
    name: str
    created: datetime
    patient_id: str

    class Config:
        alias_generator = to_camel
