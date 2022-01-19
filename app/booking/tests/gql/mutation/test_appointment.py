import pytest
from graphene import Schema
from graphene.test import Client
from graphql.execution.executors.asyncio import AsyncioExecutor

from app.booking.gql.mutation import ScheduleMutations
from app.booking.models.db import Appointment, AppointmentStatus
from app.users.common.models.db import DashboardUser as User
from core.errors import (GqlError, NotAvailableGqlError, NotFoundGqlError, ServerGqlError,
                         TitleAlreadyTakenGqlError, ValidationGqlError)
from core.errors import ErrorEnum


@pytest.fixture()
def client(doctor_context):
    yield Client(schema=Schema(mutation=ScheduleMutations, types=[
        GqlError, TitleAlreadyTakenGqlError, ServerGqlError, ValidationGqlError, NotFoundGqlError,
        NotAvailableGqlError,
    ]), context_value=doctor_context)


class TestCreateAppointment:

    @pytest.mark.parametrize("db_patients", [1], indirect=["db_patients", ])
    def test_mutate(self, db_connections, client, db_sub_org, db_patients):
        mutation_query = '''
             mutation create_appointment {{
                createAppointment(record: {{title: "{title}", eventType: CONSULTATION,
                  startDate: "{start_date}", endDate: "{end_date}", patient:"{patient_id}",
                   location: "{location_id}"}} ) {{
                  ok
                  record {{
                    title,
                    startDate
                    endDate
                    id_
                    patient {{
                      id_,
                      firstName
                      status
                    }}
                    user {{
                      id_,
                      firstName
                      status
                    }}
                    createdBy {{
                      id_,
                      firstName
                    }}
                    location {{
                       id_
                       fullAddress {{
                        city
                        }}
                      }}
                  }}
                  error {{
                    message
                  }}
                }}
            }}
            '''
        doctor_auth = client.execute_options['context_value']['request'].state.user
        doctor = User.objects.filter(cognito_sub=doctor_auth.get("sub")).first()
        patient, *_ = db_patients

        title = "appointment"
        start_date = "2025-12-22T08:30:00"
        end_date = "2025-12-22T08:45:00"

        executed = client.execute(mutation_query.format(
            title=title,
            start_date=start_date,
            end_date=end_date,
            patient_id=patient.id,
            location_id=db_sub_org.id,
        ), executor=AsyncioExecutor())

        if not executed["data"]["createAppointment"]["ok"]:
            print(executed)

        saved_appointment: Appointment = Appointment.objects.first()

        expected = {
            "createAppointment": {
                "ok": True,
                "error": None,
                "record": {
                    "id_": str(saved_appointment.id),
                    "title": title,
                    "startDate": start_date,
                    "endDate": end_date,
                    "patient": {
                        "id_": str(patient.id),
                        "firstName": patient.firstName,
                        "status": str(AppointmentStatus.AWAITING).upper()
                    },
                    "createdBy": {
                        "id_": str(doctor.id),
                        "firstName": doctor.firstName,
                    },
                    "location": {
                        "id_": str(db_sub_org.id),
                        "fullAddress": {
                            "city": db_sub_org.address.city
                        }
                    },
                    "user": {
                        "id_": str(doctor.id),
                        "firstName": doctor.firstName,
                        "status": str(AppointmentStatus.APPROVED).upper()
                    }
                }
            }
        }

        assert 'errors' not in executed
        assert dict(executed['data']) == expected

    @pytest.mark.parametrize("db_patients", [1], indirect=["db_patients", ])
    def test_timeslot_taken(self, db_connections, client, db_patients):
        mutation_query = '''
                 mutation create_appointment {{
                    createAppointment(record: {{title: "{title}", eventType: CONSULTATION,
                      startDate: "{start_date}", endDate: "{end_date}", patient:"{patient_id}"
                 }}) {{
                      ok
                      error {{
                        ... on NotAvailableError {{
                            code
                            message
                        }}
                      }}
                    }}
                }}
                '''
        patient, *_ = db_patients

        title = "appointment"
        start_date = "2025-12-22T08:30:00"
        end_date = "2025-12-22T08:45:00"

        formated_query = mutation_query.format(
            title=title,
            start_date=start_date,
            end_date=end_date,
            patient_id=patient.id,
        )
        _ = client.execute(formated_query, executor=AsyncioExecutor())
        executed2 = client.execute(formated_query, executor=AsyncioExecutor())

        assert len(Appointment.objects.all()) == 1
        assert str(ErrorEnum.NOT_AVAILABLE) in executed2["data"]["createAppointment"]["error"][
            "code"]


class TestUpdateNote:
    def test_mutate(self):
        pass


class TestDeleteAppointment:
    def test_mutate_cancel_existing(self, db_connections, client, appointment):
        appointment_id = appointment.id

        expected = {
            "cancelAppointment": {
                "ok": True,
                "error": None,
                "result": {
                    "patient": {
                        "id_": str(appointment.patients[0].id),
                        "status": str(AppointmentStatus.CANCELLED).upper()
                    },
                    "user": {
                        "id_": str(appointment.users[0].id),
                        "status": str(AppointmentStatus.CANCELLED).upper()
                    }
                }
            }
        }

        assert Appointment.objects().count() == 1

        executed = client.execute(f'''
            mutation calcl_app {{
              cancelAppointment(id_: "{appointment_id}") {{
                ok
                error {{
                  code
                  message
                }}
                result {{
                    patient {{
                        id_
                        status
                    }}
                    user {{
                        id_
                        status
                    }}
                }}
              }}
            }}
        ''', executor=AsyncioExecutor())

        assert Appointment.objects().count() == 1
        assert 'errors' not in executed
        assert executed["data"]["cancelAppointment"]["error"] is None
        assert dict(executed['data']) == expected
