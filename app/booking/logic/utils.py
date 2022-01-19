from datetime import datetime
from typing import List

from mongoengine import Q

from ..models.db import Appointment, AppointmentStatus

FREE = [AppointmentStatus.REJECTED, AppointmentStatus.CANCELLED]


async def is_timeslot_free(care_team_organizer_id, start_date: datetime,
                           end_date: datetime) -> bool:
    appointment: Appointment = (
        Appointment
            .objects()
            .filter(
            Q(users__id=care_team_organizer_id) & Q(users__status__nin=FREE)
        )
            .filter(
            (Q(startDate__gte=start_date) & Q(startDate__lt=end_date)) |
            (Q(endDate__gt=start_date) & Q(endDate__lte=end_date))
        )
            .first()
    )

    return not appointment


async def get_appointments_in_dates(care_team_organizer_id, start_date: datetime, end_date: datetime
                                    ) -> List[Appointment]:
    """Get all appointments that falls into one of the spacing."""
    appointments = (
        Appointment.objects
            .filter(Q(users__id=care_team_organizer_id) & Q(users__status__nin=FREE))
            .filter(
            (Q(startDate__gte=start_date) & Q(startDate__lte=end_date)) |
            (Q(endDate__gt=start_date) & Q(endDate__lt=end_date))
        )
            .order_by("startDate")
    )

    return appointments.all()
