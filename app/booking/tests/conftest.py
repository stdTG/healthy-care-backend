from datetime import date, datetime, time
from random import choice

import pytest

from app.booking.models.db import Appointment, AppointmentStatus, EventType, StatusInfo


@pytest.fixture(scope='module')
def appointment():
    Appointment.drop_collection()
    appointment = Appointment()

    appointment.title = 'appointment'
    appointment.eventType = choice((EventType.CONSULTATION, EventType.VACCINATION, EventType.OTHER))
    appointment.startDate = "2025-12-22T08:30:00"
    appointment.endDate = "2025-12-22T08:45:00"
    appointment.createdById = "5fd5da0d36a6434d52be193f"
    appointment.patients = [
        StatusInfo(id="1fd5da0d36a6434d52be193f", status=AppointmentStatus.APPROVED), ]
    appointment.users = [
        StatusInfo(id="5fd5da0d36a6434d52be193f", status=AppointmentStatus.APPROVED), ]
    appointment.location = None

    yield appointment.save()


@pytest.fixture(scope='module')
def appointment_collection(request):
    """
    How to use:
    @pytest.mark.parametrize("appointment_collection",
        [{<date>: [(<time>, <time>), (...), ],}], indirect=["appointment_collection", ])
    """
    Appointment.drop_collection()

    dates, doctor_ids = request.param
    appointments = []

    for str_date, times in dates.items():
        for time_set in times:
            start_time, end_time = time_set
            appointment = Appointment()

            appointment.title = 'appointment'
            appointment.eventType = choice(
                (EventType.CONSULTATION, EventType.VACCINATION, EventType.OTHER))
            appointment.startDate = datetime.combine(date.fromisoformat(str_date),
                                                     time.fromisoformat(start_time))
            appointment.endDate = datetime.combine(date.fromisoformat(str_date),
                                                   time.fromisoformat(end_time))
            appointment.createdById = "5fd5da0d36a6434d52be193f"
            appointment.patients = [
                StatusInfo(id="1fd5da0d36a6434d52be193f", status=AppointmentStatus.APPROVED), ]
            appointment.users = [
                StatusInfo(id=choice(doctor_ids), status=AppointmentStatus.APPROVED), ]
            appointment.location = None
            appointment.save()

            appointments.append(appointment)

    yield appointments


@pytest.mark.parametrize("appointment_collection", [({"2025-12-22": [("08:30", "08:45"),
                                                                     ("08:45", "09:00")],
                                                      "2025-12-23": [("08:00", "08:15"),
                                                                     ]},
                                                     ["1fd5da0d36a6434d52be193f",
                                                      "2fd5da0d36a6434d52be193f",
                                                      "3fd5da0d36a6434d52be193f"])],
                         indirect=["appointment_collection", ])
def test_appointment_collection(db_connections, appointment_collection):
    print(appointment_collection)
