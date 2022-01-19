from datetime import date, time, datetime
import mongoengine
import pytest
from starlette.requests import Request
from random import choice
from app.booking.models.db import Appointment, AppointmentStatus, EventType, StatusInfo
from app.user_roles import Roles
from app.users.common.models.db import DashboardUser as User
from app.users.tests.conftest import db_users, working_hours
from web.cloudauth.auth_claims import AuthClaims
from web.startup.graphql import create_loaders
from tests.database.conftest import db_connections
from app.booking.tests.conftest import appointment_collection
from app.booking.logic import get_free_timeslots_for_day
from app.user_roles import Roles
expected = [
    [("08:30", "08:45"), ("08:45", "09:00")],
    [("08:30", "08:45"), ("19:45", "20:00")],
    [("08:30", "08:45"), ("09:50", "10:50"), ("19:45", "20:00")],
]

testdata = [
    (
        ({"2025-12-22": expected[0], },
         ["1fd5da0d36a643e193f4d52b", ]),
        (1, Roles.DOCTOR,),
        expected[0]
    ),
    (
        ({"2025-12-22": expected[1], },
         ["1fd5da0d36a643e193f4d52b", ]),
        (1, Roles.DOCTOR,),
        expected[1]
    ),
    (
        ({"2025-12-22": expected[2], },
         ["1fd5da0d36a643e193f4d52b", ]),
        (1, Roles.DOCTOR,),
        [("08:30", "08:45"), ("09:45", "10:00"), ("10:00", "10:15"), ("10:15", "10:30"),
         ("10:30", "10:45"),
         ("10:45", "11:00"), ("19:45", "20:00")]
    )
]


@pytest.mark.asyncio
@pytest.mark.parametrize("appointment_collection, db_users, expected", testdata,
                         indirect=["appointment_collection", "db_users"]
                         )
async def test_timeslot_for_day(db_connections, appointment_collection, db_users, working_hours,
                                expected):
    doctor, = db_users
    doctor.id = "1fd5da0d36a643e193f4d52b"
    doctor.workingHours = working_hours
    doctor.save()

    expected_slots = []
    for time_set in expected:
        start_time, end_time = time_set
        start_date = datetime.combine(date.fromisoformat("2025-12-22"),
                                      time.fromisoformat(start_time))
        end_date = datetime.combine(date.fromisoformat("2025-12-22"), time.fromisoformat(end_time))
        expected_slots.append((start_date, end_date))

    print(expected_slots)

    slots = await get_free_timeslots_for_day(doctor, None, date.fromisoformat("2025-12-22"))
    actual_slots = []
    for slot in slots:
        actual_slots.append((slot.start_time, slot.end_time))

    assert not set(expected_slots).issubset(set(actual_slots))

    for exp_slot in expected_slots:
        assert exp_slot not in actual_slots
