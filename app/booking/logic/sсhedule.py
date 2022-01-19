from datetime import date, datetime, time, timedelta
from typing import List

from app.models.db import WorkingHours
from app.org_units.model_db import OrgUnit
from app.users.common.models.db import DashboardUser
from .entity import Timeslot
from .utils import get_appointments_in_dates


async def get_free_timeslots_for_day(user: DashboardUser, master_org: OrgUnit, curr_date: date, ):
    free_slots = []
    duration = user.duration

    # get user`s schedule
    working_hours = get_working_hours(user, master_org)
    if not working_hours:
        return free_slots

    today = date.today()
    if today > curr_date:
        return free_slots

    # check what day is work day
    weekday = curr_date.weekday()
    working_hours_for_day = [wh for wh in working_hours if wh.dayOfWeek == weekday]
    if not working_hours_for_day:
        return free_slots

    working_hours_for_day, = working_hours_for_day
    curr_date = datetime.combine(curr_date,
                                 time.fromisoformat(working_hours_for_day.startTime)).replace(
        tzinfo=None)
    end_date = datetime.combine(curr_date,
                                time.fromisoformat(working_hours_for_day.endTime)).replace(
        tzinfo=None)
    hours = (curr_date, end_date)

    # appointments for day
    appointments = await get_appointments_in_dates(user.id, curr_date, end_date)

    # all busy times
    busy = []
    for appointment in appointments:
        busy.append((appointment.startDate, appointment.endDate,))

    start_lunch_date = datetime \
        .combine(curr_date, time.fromisoformat(working_hours_for_day.startLunchTime)) \
        .replace(tzinfo=None)
    end_lunch_date = datetime \
        .combine(curr_date, time.fromisoformat(working_hours_for_day.endLunchTime)) \
        .replace(tzinfo=None)
    busy.append((start_lunch_date, end_lunch_date))

    return get_slots(hours, busy, timedelta(minutes=duration))


def get_slots(hours, appointments, duration=timedelta(minutes=20)) -> List[Timeslot]:
    result = []
    slots = sorted([(hours[0], hours[0])] + appointments + [(hours[1], hours[1])])
    for start, end in ((slots[i][1], slots[i + 1][0]) for i in range(len(slots) - 1)):
        # assert start <= end, "Cannot attend all appointments"
        while start + duration <= end:
            result.append(Timeslot(start_time=start, end_time=start + duration))
            start += duration

    return result


def get_working_hours(user: DashboardUser, master_org: OrgUnit) -> List[WorkingHours]:
    working_hours = user.workingHours
    if not working_hours:
        if user.orgUnitId:
            org_unit: OrgUnit = OrgUnit.objects(pk=user.orgUnitId).first()
            working_hours = org_unit.workingHours

        if not working_hours:
            working_hours = master_org.workingHours

    return working_hours
