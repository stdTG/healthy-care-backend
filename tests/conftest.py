import asyncio
from collections import namedtuple

import pytest

from app.tenant_workspaces.model_db import WorkspaceDb
from core.cognito import CognitoUserPoolClients, CognitoUserPools
from core.config import get_app_config
from core.utils.db import register_master_connection, register_tenant_connection

# Dell
permanent_user_pool_id = "eu-west-1_CXFFRr7hr"
permanent_client_id = "4q7jmvp7d4ruh2uj2sarmqepaq"

# permanent_user_pool_id = None
# permanent_client_id = None


class TestContext:
    base_url = "http://localhost:8000"
    cfg = get_app_config()

    def get_url(self, path: str) -> str:
        return f"{self.base_url}{path}"


@pytest.fixture(scope="session")
def ctx():
    yield TestContext()


@pytest.fixture(scope="session")
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def db(ctx, loop):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(register_master_connection(ctx.cfg))

    db1 = WorkspaceDb(**{"host_alias": "tenant-host-1", "db_name": "ignilife_1"})
    db2 = WorkspaceDb(**{"host_alias": "tenant-host-1", "db_name": "ignilife_2"})
    loop.run_until_complete(register_tenant_connection(ctx.cfg, db1, "tenant-db-basic-data"))
    loop.run_until_complete(register_tenant_connection(ctx.cfg, db2, "tenant-db-personal-data"))


AwsContext = namedtuple("AwsContext", ["region", "user_pool_id", "user_pool_client_id"])


@pytest.fixture(scope="session")
def aws_ctx(ctx):
    region = ctx.cfg.AWS_REGION_NAME
    user_pools = CognitoUserPools(region)

    def create_user_pool(full_name, user_pool_name, ctx: TestContext, region, user_pools):
        user_pools_clients = CognitoUserPoolClients(region)

        print("Creating Cognito User Pool")
        user_pool_id = user_pools.create(full_name, f"{ctx.cfg.ENVIRONMENT_NAME}-{user_pool_name}")
        print(f"UserPool.Id: {user_pool_id}")

        user_pool_client_id = user_pools_clients.create(user_pool_id, "test-client")
        return AwsContext(region, user_pool_id, user_pool_client_id)

    def result():
        if permanent_user_pool_id and permanent_client_id:
            user_pool_id = permanent_user_pool_id
            user_pool_client_id = permanent_client_id
            print(f"Reusing PERMANENT UserPool. Id: {user_pool_id}")
            return AwsContext(ctx.cfg.AWS_REGION_NAME, user_pool_id, user_pool_client_id)
        else:
            create_user_pool("Permanent Test UserPool", "PERMANENT-FOR-TESTS", ctx, region,
                             user_pools)

        temp = create_user_pool("Temp Test UserPool", "TEMP-FOR-TESTS", ctx, region, user_pools)
        print(f"Created TEMP UserPool. Id: {temp.user_pool_id}")
        return temp

    aws_context = result()
    yield aws_context

    if permanent_user_pool_id and permanent_client_id:
        pass
    else:
        print("Deleting Cognito User Pool")
        user_pools.delete(aws_context.user_pool_id)
