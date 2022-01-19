from datetime import datetime

from pydantic import BaseModel


class Timeslot(BaseModel):
    start_time: datetime
    end_time: datetime
