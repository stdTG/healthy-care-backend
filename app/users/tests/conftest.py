from typing import List

import pytest
from starlette.requests import Request

from app.user_roles.model import Roles
from app.users.common.models.db import DashboardUser as User, PatientUser as Patient
from tests.database.conftest import db_connections
from web.cloudauth.auth_claims import AuthClaims
from .utils import generate_patients, generate_user, generate_users
from ...models.db import DayOfWeek, WorkingHours


@pytest.fixture()
def db_users(request) -> List[User]:
    count, role = request.param
    users_info = generate_users(users_num=count, role=role)
    users = []
    for num, user_info in enumerate(users_info):
        users.append(
            User(
                **user_info,
                cognito_sub=f"a34a9798-faec-41fa-92ed-88ef3c4da93{num}",
            ).save()
        )
    yield users


@pytest.fixture()
def db_patients(request) -> List[Patient]:
    count = request.param
    patient_info = generate_patients(users_num=count)
    patients = []
    for num, user_info in enumerate(patient_info):
        patients.append(
            Patient(
                **user_info,
                cognito_sub=f"a34a9798-faec-41fa-92ed-88ef3c4da93{num}",
            ).save()
        )
    yield patients


@pytest.fixture()
def working_hours():
    yield [WorkingHours(
        dayOfWeek=DayOfWeek.MONDAY,
        startTime="08:00",
        endTime="20:00",
        startLunchTime="13:00",
        endLunchTime="14:00",
    ), WorkingHours(
        dayOfWeek=DayOfWeek.TUESDAY,
        startTime="08:00",
        endTime="20:00",
        startLunchTime="13:00",
        endLunchTime="14:00",
    ), WorkingHours(
        dayOfWeek=DayOfWeek.WEDNESDAY,
        startTime="08:00",
        endTime="20:00",
        startLunchTime="13:00",
        endLunchTime="14:00",
    ), WorkingHours(
        dayOfWeek=DayOfWeek.THURSDAY,
        startTime="08:00",
        endTime="20:00",
        startLunchTime="13:00",
        endLunchTime="14:00",
    ), WorkingHours(
        dayOfWeek=DayOfWeek.FRIDAY,
        startTime="08:00",
        endTime="20:00",
        startLunchTime="13:00",
        endLunchTime="14:00",
    )]


@pytest.fixture()
def doctor_context(working_hours):
    from web.startup.graphql import create_loaders

    user_info = generate_user(role=Roles.DOCTOR)
    doctor = User(
        **user_info,
        cognito_sub=f"a34a9798-faec-41fa-92ed-88ef3c4da531",
        workingHours=working_hours
    )
    doctor.save()

    request = Request(scope={
        'type': 'http',
        'state': {
            'user': {
                "roles": [Roles.DOCTOR],
                "sub": doctor.cognito_sub,
            },
            'auth_claims': AuthClaims(sub=doctor.cognito_sub, username=doctor.cognito_sub),
            'loaders': create_loaders()
        }
    })
    context = {
        'request': request
    }
    yield context


@pytest.mark.parametrize("db_users", [(5, Roles.DOCTOR,)], indirect=["db_users", ])
def test_generate_doctors(db_connections, db_users: List[User], doctor_context):
    assert len(db_users) == 5
    assert len(User.objects.all()) == 5
    for user in db_users:
        assert user.role == Roles.DOCTOR

@pytest.mark.parametrize("db_patients", [5], indirect=["db_patients", ])
def test_generate_patients(db_connections, db_patients: List[Patient]):
    assert len(db_patients) == 5
    for user in db_patients:
        assert user.role == Roles.PATIENT
