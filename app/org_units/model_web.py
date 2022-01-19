from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.web import Address
from core.utils.strings import to_camel


class OrgUnit(BaseModel):
    id: Optional[str] = None
    parent_id: Optional[str] = None
    short_name: str
    full_name: str
    is_care_team: bool = False

    class Config:
        alias_generator = to_camel


class Interval(BaseModel):
    startTime: time = "%H:%M"
    endTime: time = "%H:%M"


class WorkingHours(BaseModel):
    day: int
    interval: Optional[Interval]

    @classmethod
    def from_db(cls, db_wh):
        interval = Interval(
            startTime=datetime.strptime(db_wh.startTime, "%H:%M").time(),
            endTime=datetime.strptime(db_wh.endTime, "%H:%M").time()
        )

        return cls(
            day=db_wh.dayOfWeek,
            interval=interval,
        )


class HealthCenter(BaseModel):
    id: str
    title: str
    description: Optional[str]
    site: Optional[str]
    address: Optional[Address]
    phoneNumber: Optional[List[str]]
    schedule: Optional[List[WorkingHours]]


class CareTeamMember(BaseModel):
    id: str = Field(example="5fb254a78d187c15019ef7c9")
    firstName: str = Field(example="John")
    lastName: str = Field(example="Doe")
    role: str = Field(example="doctor")
    speciality: Optional[str] = Field(example="doctor")
    avatar: Optional[str] = Field(
        example="https://alakine.s3-eu-west-1.amazonaws.com/alakine-oleg-ignilife/patient/"
                "5faa2ba1f5e801063242e144/profile_photo.jpg")


class CareTeamMembers(BaseModel):
    careTeamId: str = Field(example="5fb254b78d187c15019ef7c3")
    members: Optional[List[CareTeamMember]]


class CareTeams(BaseModel):
    careTeamMembers: Optional[List[CareTeamMembers]]
