from app.tenant_workspaces.model_db import Workspace
from core import config
from core.cognito import CognitoUserPools
from core.sendbird.applications import Applications
from core.utils.aws import get_s3
from .utils import drop_database


class DropWorkspace:

    def __init__(self):
        self.c_user_pools = CognitoUserPools()

    async def execute(self, short_name: str):

        print('Deleting workspace: %s' % short_name)
        wks: Workspace = Workspace.objects(short_name=short_name).first()
        if not wks:
            return {"result": "Not found"}

        drop_database(wks.tenant_db_1)
        drop_database(wks.tenant_db_2)

        self.c_user_pools.delete(wks.cognito.user_pool_id)
        self.delete_s3(wks.s3.name, wks.s3.aws_region)
        await self.delete_sendbird(wks.short_name)

        wks.delete()

        return {"result": "OK"}

    def delete_s3(self, bucket_name, region):
        s3_client = get_s3(region)
        s3_client.delete_bucket(Bucket=bucket_name)

    async def delete_sendbird(self, wks_name):
        cfg = config.get_app_config()
        application_service = Applications(cfg.SENDBIRD_ORGANIZATION_API_TOKEN)
        await application_service.delete(
            app_id=f"{wks_name}",
        )
