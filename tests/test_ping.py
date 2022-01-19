import pytest
import requests


@pytest.mark.skip()
def test_ping(ctx):
    url = ctx.get_url("/ping")
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
