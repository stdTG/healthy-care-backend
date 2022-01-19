import mongoengine
import pytest


@pytest.fixture(scope='module')
def db_connections():
    names = ["master-db", "tenant-db-basic-data", "tenant-db-personal-data"]

    yield {
        name: mongoengine.connect(db="test-db", host="mongomock://localhost", alias=name) for name
        in names
    }

    [mongoengine.disconnect(alias=name) for name in names]
