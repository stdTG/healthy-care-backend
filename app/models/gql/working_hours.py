from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..db import WorkingHours as DbWorkingHours

import graphene

from .day_of_week import DayOfWeek


class WorkingHours(graphene.ObjectType):
    dayOfWeek = DayOfWeek()

    startTime = graphene.Time()
    endTime = graphene.Time()

    startLunchTime = graphene.Time()
    endLunchTime = graphene.Time()

    @classmethod
    def from_db(cls, db_working_hours: DbWorkingHours):
        return cls(
            dayOfWeek=DayOfWeek.get(db_working_hours.dayOfWeek),
            startTime=graphene.Time.parse_value(db_working_hours.startTime),
            endTime=graphene.Time.parse_value(db_working_hours.endTime),
            startLunchTime=graphene.Time.parse_value(db_working_hours.startLunchTime),
            endLunchTime=graphene.Time.parse_value(db_working_hours.endLunchTime),
        )


class WorkingHoursInput(graphene.InputObjectType):
    dayOfWeek = DayOfWeek(required=True)

    startTime = graphene.Time(required=True)
    endTime = graphene.Time(required=True)

    startLunchTime = graphene.Time(required=True)
    endLunchTime = graphene.Time(required=True)


class AddWorkingHoursInput(graphene.InputObjectType):
    working_hours = graphene.List(graphene.NonNull(WorkingHoursInput), required=True)
