import pytest
import requests

from core.utils.random import Random
from core.utils.strings import dict_w_camel_keys


@pytest.fixture(scope="module")
def db_host_sample():
    x = Random.get()
    data = dict_w_camel_keys({
        "alias": f"autogenerated-{x.short_code}",
        "name": "Autogenerated Tenant Host",
        "description": "",
        "connection_string_format": "mongodb://{host}/{dbname}",
        "db_host": "localhost",
        "db_user": "local_user",
        "db_password": "local_user_password"
    })
    yield data


@pytest.mark.asyncio
async def test_create(ctx, db_host_sample):
    print(db_host_sample)
    url = ctx.get_url("/db_hosts")
    response = requests.post(url, json=db_host_sample)
    print(response.text)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_list(ctx):
    url = ctx.get_url("/db_hosts")
    response = requests.get(url)
    print(response.text)
    assert response.status_code == 200
