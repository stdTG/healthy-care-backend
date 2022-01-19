from datetime import date

from fastapi import Request

from app.context import get_current_master_org
from app.users.common.models.db import DashboardUser
from core.errors import HTTPNotFoundError
from .router import router_mobile
from ..logic.sсhedule import get_free_timeslots_for_day
from ..models.db import Appointment
from ..models.web import Timeslots


@router_mobile.get("/{appointment_id}/timeslot/available-slots", response_model=Timeslots)
async def get_timeslots_by_appointment(request: Request, appointment_id):
    appointment: Appointment = Appointment.objects.with_id(appointment_id)
    if not appointment:
        raise HTTPNotFoundError(message=f"Appointment not found [{appointment_id}]")

    master_workspace = await get_current_master_org(request)
    user = DashboardUser.objects.with_id(appointment.users[0].id)
    curr_date = appointment.startDate.date()

    timeslots = await get_free_timeslots_for_day(user, master_workspace, curr_date)
    return Timeslots(slots=[ts.start_time for ts in timeslots])


@router_mobile.get("/{dashboard_user_id}/timeslot/{date}", response_model=Timeslots)
async def get_timeslots_by_dashboard_user(request: Request, dashboard_user_id, date: date):
    user = DashboardUser.objects.with_id(dashboard_user_id)
    if not user:
        raise HTTPNotFoundError(message=f"User not found [{dashboard_user_id}]")

    master_workspace = await get_current_master_org(request)
    timeslots = await get_free_timeslots_for_day(user, master_workspace, date)

    return Timeslots(slots=[ts.start_time for ts in timeslots])
