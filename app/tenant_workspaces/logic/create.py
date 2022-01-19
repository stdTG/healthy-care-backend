import json
import re

import mongoengine
import pymongo

from app.org_units.model_db import OrgUnit
from app.tenant_db_hosts.model_db import DbHost
from app.user_roles.logic import Create as UserRolesCreate
from app.user_roles.model import Roles
from core.cognito import CognitoUserPoolClients, CognitoUserPools, CognitoUsers
from core.config import get_app_config
from core.errors import *
from core.sendbird.applications import Applications
from core.sendbird.users import SendbirdUsers
from core.utils.aws import get_s3
from core.utils.transaction import Transaction
from .utils import create_database, drop_database
from ..model_db import Workspace, WorkspaceDb, WorkspaceSendbird
from ..model_web import Workspace as WebWorkspace
from ...users.common.models.db import CognitoUser, SendbirdSettings
from ...users.dashboard.logic.user import create_dashboard_user_handler


class Create:
    c_users = CognitoUsers()
    c_user_pools = CognitoUserPools()
    c_pool_clients = CognitoUserPoolClients()

    def __init__(self, input_: WebWorkspace, make_super_admin=False, ):
        self.cfg = get_app_config()

        self.input_ = input_
        self.make_super_admin = make_super_admin
        self.user_pool_name = f"{self.cfg.ENVIRONMENT_NAME}-{self.input_.shortName}"

    @staticmethod
    def exists(short_name):
        print("[APP] Checking that workspace exists")
        db_object: Workspace = Workspace.objects(short_name=short_name).first()
        return db_object is not None

    async def tenant(self):

        with Transaction("CreateTenantWorkspace") as ctx:
            self.create_user_pool()
            ctx.push(self.rollback_create_user_pool)

            self.create_tenant_db()
            ctx.push(self.rollback_create_tenant_db)

            self.create_workspace_record()
            ctx.push(self.rollback_create_workspace_record)

            self.create_s3()
            ctx.push(self.rollback_create_s3)

            await self.register_tenant_connections()
            await self.create_tenant_admin()

            await self.create_sendbird()

            self.create_orgunit_record()

            ctx.commitAll()

        return self.workspace

    async def create_system_user(self):
        sendbird: WorkspaceSendbird = self.workspace.sendbird
        users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)

        full_name = f"system_user"

        sb_user = await users_client.create(user_id=self.cfg.SENDBIRD_SYSTEM_ACCOUNT,
                                            nickname=full_name, profile_url="",
                                            issue_access_token=True, issue_session_token=True)

        sendbird.system_user.access_token = sb_user.data["access_token"]
        sendbird.system_user.user_id = self.cfg.SENDBIRD_SYSTEM_ACCOUNT
        sendbird.system_user.nickname = full_name

    async def create_sendbird(self):
        application_service = Applications(self.cfg.SENDBIRD_ORGANIZATION_API_TOKEN)
        meta_info = await application_service.create(
            app_name=f"{self.cfg.ENVIRONMENT_NAME}-{self.workspace.short_name}",
            region_key="frankfurt-1",
        )

        await self.create_system_user()

        self.workspace.sendbird.app_id = meta_info.data["app_id"]
        self.workspace.sendbird.app_name = meta_info.data["app_name"]
        self.workspace.sendbird.master_api_token = meta_info.data["api_token"]
        self.workspace.sendbird.master_api_token_created = meta_info.data["created_at"]
        self.workspace.sendbird.region = meta_info.data["region"]["region_key"]
        self.workspace.save()

    async def master(self):

        with Transaction("CreateMasterWorkspace") as ctx:
            ctx.push(self.rollback_create_master_db)
            self.create_user_pool()
            ctx.push(self.rollback_create_user_pool)

            self.create_tenant_db()
            ctx.push(self.rollback_create_tenant_db)

            self.create_workspace_record()

            self.create_s3()
            ctx.push(self.rollback_create_s3)

            await self.register_tenant_connections()
            await self.create_tenant_admin()

            self.create_orgunit_record()

            ctx.commitAll()

        return self.workspace

    async def register_tenant_connections(self):
        async def register_tenant_connection(workspace_db: WorkspaceDb, alias="default"):
            db: DbHost = DbHost.objects(alias=workspace_db.host_alias).first()

            mongoengine.disconnect(alias)
            mongoengine.register_connection(
                alias=alias,
                host=db.get_db_connection_string(workspace_db.db_name)
            )

        await register_tenant_connection(self.workspace.tenant_db_1, "tenant-db-basic-data")
        await register_tenant_connection(self.workspace.tenant_db_2, "tenant-db-personal-data")

    def create_user_pool(self):
        print("[APP] Creating user pool...")
        self.user_pool_id = self.c_user_pools.create(self.input_.shortName, self.user_pool_name)

        print("[APP] Creating client DASHBOARD...")
        self.dashboard_client_id = self.c_pool_clients.create(self.user_pool_id, "dashboard")

        print("[APP] Creating client MOBILE...")
        self.mobile_client_id = self.c_pool_clients.create(self.user_pool_id, "mobile")

        # [COGNITO] Init Roles
        print("[APP] Creating initialising ROLES...")
        UserRolesCreate().default_roles(self.user_pool_id, self.make_super_admin)

    def rollback_create_user_pool(self):
        print("[ROLLBACK] create_user_pool")
        self.c_user_pools.delete(self.user_pool_id)

    def create_tenant_db(self):
        print("[APP] Creating tenant databases...")

        def init_workspace_db_record(host_alias: str, db_name: str):
            obj = DbHost.objects(alias=host_alias).first()
            if not obj:
                raise HTTPNotFoundError(f"DB Host Definition not found: {host_alias}")

            wdb = WorkspaceDb()
            wdb.host_alias = host_alias
            wdb.db_name = db_name
            return wdb

        self.tenant_db_1 = init_workspace_db_record(self.input_.dbHosts.hostAlias1,
                                                    Workspace.get_db_name_1(self.input_.shortName))
        self.tenant_db_2 = init_workspace_db_record(self.input_.dbHosts.hostAlias2,
                                                    Workspace.get_db_name_2(self.input_.shortName))

        create_database(self.tenant_db_1)
        create_database(self.tenant_db_2)

    def rollback_create_tenant_db(self):
        print("[ROLLBACK] create_tenant_db")

        drop_database(self.tenant_db_1)
        drop_database(self.tenant_db_2)

    def rollback_create_master_db(self):
        print("[ROLLBACK] create_master_db")

        connection = get_app_config().MASTER_DB_CONNECTION
        try:
            db_uri, db_name = re.search(r"(.*/)(\w*$)", connection).groups()
            client = pymongo.MongoClient(db_uri)
            client.drop_database(db_name)

        except Exception as error:
            print(str(error))

    async def create_tenant_admin(self):

        # [COGNITO] Init ADMIN user
        print("[APP] Creating ADMIN user...")

        role = Roles.SUPER_ADMIN if self.make_super_admin else Roles.ADMIN
        if self.make_super_admin:
            print("[APP] Making ADMIN super_admin...")

        user_input = CognitoUser(
            email=self.input_.admin.email,
            phone=self.input_.admin.phoneNumber,
            password=self.input_.admin.password,
            send_sms=True if self.input_.admin.phoneNumber else False,
            send_email=True if self.input_.admin.email else False,
            role=role,
            orgUnitId=None,
        )

        self.db_admin = await create_dashboard_user_handler(user_input, self.workspace)

    def create_workspace_record(self):

        # [MASTER_DB] Store all workspace settings
        wks = Workspace()

        wks.human_friendly_name = self.input_.fullName
        wks.short_name = self.input_.shortName
        wks.admin_email = self.input_.admin.email
        wks.admin_phone_number = self.input_.admin.phoneNumber

        wks.tenant_db_1 = self.tenant_db_1
        wks.tenant_db_2 = self.tenant_db_2

        wks.aws_region = self.input_.awsRegion
        wks.cognito.user_pool_id = self.user_pool_id
        wks.cognito.dashboard_client_id = self.dashboard_client_id
        wks.cognito.mobile_client_id = self.mobile_client_id

        wks.save()

        self.workspace = wks

    def create_orgunit_record(self):
        org_unit = OrgUnit.create_master_org(self.input_.fullName, default_working_hours=True)
        org_unit.save()

        self.org_unit = org_unit

    def rollback_create_workspace_record(self):
        if hasattr(self, "workspace"):
            self.workspace.delete()
        else:
            Workspace.objects(short_name=self.input_.shortName).delete()

    def create_s3(self):
        print("[APP] Creating s3 bucket...")

        region = self.input_.awsRegion
        bucket_name = f"{self.cfg.ENVIRONMENT_NAME}-{self.input_.shortName}"
        s3_client = get_s3(region)
        location = {'LocationConstraint': region}

        s3_client.create_bucket(Bucket=bucket_name,
                                ACL="public-read",
                                CreateBucketConfiguration=location)
        bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': '*',
                'Action': ['s3:GetObject'],
                'Resource': f"arn:aws:s3:::{bucket_name}/*"
            }]
        }
        bucket_policy = json.dumps(bucket_policy)
        s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

        self.workspace.s3.region = region
        self.workspace.s3.name = bucket_name

    def rollback_create_s3(self):
        bucket_name = f"{self.cfg.ENVIRONMENT_NAME}-{self.input_.shortName}"
        region = self.input_.awsRegion
        s3_client = get_s3(region)

        s3_client.delete_bucket(Bucket=bucket_name)
