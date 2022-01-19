import pytest
from graphene import Schema
from graphene.test import Client
from graphql.execution.executors.asyncio import AsyncioExecutor

from app.booking.gql.query import ScheduleQueries
from app.booking.models.db import Appointment
from app.users.common.models.db import DashboardUser as User

testdata = [
    ({**{f"2025-02-0{i}": [("08:30", "08:45")] for i in range(1, 10)},
      **{f"2025-02-{i}": [("08:30", "08:45")] for i in range(10, 29)},
      "2025-03-01": [("08:30", "08:45")]},
     ["1fd5da0d36a643e193f4d52b", ]),
]


@pytest.fixture()
def client(doctor_context):
    yield Client(schema=Schema(query=ScheduleQueries), context_value=doctor_context)


@pytest.mark.parametrize("appointment_collection", testdata,
                         indirect=["appointment_collection"]
                         )
def test_query_events_by_interval(db_connections, client, appointment_collection):
    doctor_auth = client.execute_options['context_value']['request'].state.user
    doctor = User.objects.filter(cognito_sub=doctor_auth.get("sub")).first()
    for app in appointment_collection:
        app.users[0].id = doctor.id
        app.save()

    query = '''{
          eventMany(filter: {startDate: "2025-02-01", endDate: "2025-02-28"}) {
              items {
                ... on Appointment {
                title
                }
              }
          }
    }
    '''

    executed = client.execute(query, executor=AsyncioExecutor())
    appointment_count = Appointment.objects.count() - 1  # one appointment for next month

    assert len(executed["data"]["eventMany"]["items"]) == appointment_count
