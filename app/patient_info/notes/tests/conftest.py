from datetime import datetime

import mongoengine
import pytest
from starlette.requests import Request

from app.patient_info.notes.models.db import Note as DbNote
from app.users.common.models.db import DashboardUser as DbDashboardUser
from web.cloudauth.auth_claims import AuthClaims
from web.startup.graphql import create_loaders

mongoengine.connect('test-db', host='mongomock://localhost', alias='default')
mongoengine.connect('test-db', host='mongomock://localhost', alias='master-db')
mongoengine.connect('test-db', host='mongomock://localhost', alias='tenant-db-basic-data')
mongoengine.connect('test-db', host='mongomock://localhost', alias='tenant-db-personal-data')


@pytest.fixture(scope='module')
def db_dashboard_user():
    DbDashboardUser.drop_collection()
    yield DbDashboardUser(
        cognito_sub='a34a9798-faec-41fa-92ed-88ef3c4da935',
        firstName='anon',
        lastName='anon',
        email='hello@hello.com',
        role='admin'
    ).save()


@pytest.fixture(scope='module')
def context(db_dashboard_user):
    request = Request(scope={
        'type': 'http',
        'state': {
            'user': db_dashboard_user,
            'auth_claims': AuthClaims(sub=db_dashboard_user.cognito_sub,
                                      username=db_dashboard_user.cognito_sub),
            'loaders': create_loaders()
        }
    })
    context = {
        'request': request
    }
    yield context


@pytest.fixture(scope='module')
def db_note(db_dashboard_user):
    DbNote.drop_collection()
    yield DbNote(
        title='title',
        content='content',
        createdById=db_dashboard_user.id,
        patientId='5fd5da0d36a6434d52be193f',
        createdAt=datetime.now(),
        updatedAt=None
    ).save()


@pytest.fixture(scope='module')
def db_notes_collection(db_dashboard_user):
    DbNote.drop_collection()
    yield [DbNote(
        title=f'title_{i + 1}',
        content=f'content_{i + 1}',
        createdById=db_dashboard_user.id,
        patientId='5fd5da0d36a6434d52be193f',
        createdAt=datetime.now(),
        updatedAt=None
    ).save() for i in range(15)]
