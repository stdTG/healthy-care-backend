from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gql import WorkingHoursInput

from mongoengine import EmbeddedDocument
from mongoengine.fields import StringField, IntField


class WorkingHours(EmbeddedDocument):
    dayOfWeek = IntField()
    startTime = StringField()
    endTime = StringField()

    startLunchTime = StringField()
    endLunchTime = StringField()

    @classmethod
    def from_gql(cls, gql_working_hours: WorkingHoursInput) -> WorkingHours:
        return cls(
            dayOfWeek=gql_working_hours.dayOfWeek,
            startTime=str(gql_working_hours.startTime),
            endTime=str(gql_working_hours.endTime),
            startLunchTime=str(gql_working_hours.startLunchTime),
            endLunchTime=str(gql_working_hours.endLunchTime),
        )
