import faker
import pytest

from app.org_units.model_db import OrgUnit

fake = faker.Faker()


@pytest.fixture(scope='module')
def db_sub_org():
    json = {
        "name": "sub_org",
        "phone": fake.phone_number(),
        "email": fake.email(),
        "address": {
            "city": fake.city(),
            "address": fake.address(),
            "zipcode": fake.zipcode(),
            "country": fake.country(),
        },
    }

    yield OrgUnit(**json).save()
