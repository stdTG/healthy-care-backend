from datetime import datetime
from typing import List

from pydantic import BaseModel


class Timeslots(BaseModel):
    slots: List[datetime]
