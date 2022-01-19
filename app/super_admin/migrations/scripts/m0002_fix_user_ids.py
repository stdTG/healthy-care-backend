from app.tenant_workspaces.model_db import (Workspace as DbWorkspace,
                                            WorkspaceAwsCognito as DbWorkspaceAwsCognito)
from app.users.common.models.db import (DashboardUser as DbDashboardUser,
                                        PatientUser as DbPatientUser)
from core.cognito import CognitoGroups, CognitoUser, CognitoUsers
from core.sendbird.users import SendbirdUsers
from core.utils.aws import get_boto3_client
from web.startup.db_and_tenant import register_tenant_dbs

__log = []
__cognito_users_client: CognitoUsers = None
__cognito_groups_client: CognitoGroups = None


async def run(**args):
    global __cognito_users_client
    global __cognito_groups_client

    for obj in DbWorkspace.objects():
        wks: DbWorkspace = obj
        cgt: DbWorkspaceAwsCognito = wks.cognito
        # client = get_boto3_client("cognito-idp", cgt.aws_region)

        await register_tenant_dbs(wks)
        __cognito_users_client = CognitoUsers(aws_region=cgt.aws_region)
        __cognito_groups_client = CognitoGroups(aws_region=cgt.aws_region)

        await __fix_users_in_workspace(wks, cgt)

    return __log


async def __fix_dashboard_users(wks: DbWorkspace, cgt: DbWorkspaceAwsCognito,
                                cgt_user: CognitoUser):
    print(cgt_user.sub)
    groups = __cognito_groups_client.admin_list_groups_for_user(username=cgt_user.sub,
                                                                user_pool_id=cgt.user_pool_id)[
        "groups"]

    print(groups)
    if len(groups) == 0:
        # set a group to cognito user
        # set a group to db user
        pass

    db_user: DbDashboardUser = DbDashboardUser.objects(email=cgt_user.sub).first()
    if not db_user:
        __log.append("User not found")
        __log.append(cgt_user)
        db_user = DbDashboardUser()

        # db_user.firstName = cgt_user
        # db_user.lastName = gql_user.lastName

        # if gql_user.byPhone:
        #    db_user.phone = gql_user.byPhone.phone

        # if gql_user.byEmail:
        #    db_user.email = gql_user.byEmail.email

        # db_user.role = gql_user.role
        # db_user.orgUnitId = gql_user.orgUnitId

    # __log.append(user)
    if not db_user.cognito_sub:
        __log.append(f"User [{db_user.email}] doesn't have cognito_sub")


async def __fix_patient_users(wks: DbWorkspace, cgt: DbWorkspaceAwsCognito, cgt_user: CognitoUser):
    print(f"Fixing {cgt_user.email}")
    db_user: DbPatientUser = DbPatientUser.objects(email=cgt_user.email).first()

    if not db_user:
        print(f"{cgt_user.email} not found as Patient")
        return

    client = SendbirdUsers(wks.sendbird.app_id, wks.sendbird.api_token)
    result = await client.read(user_id=cgt_user.sub)
    print(result.data)

    # save to DB
    db_user.cognito_sub = cgt_user.sub
    db_user.save()


async def __fix_users_in_workspace(wks: DbWorkspace, cgt: DbWorkspaceAwsCognito):
    cognito_users = __cognito_users_client.list_users(user_pool_id=cgt.user_pool_id)

    for cgt_user in cognito_users:
        print(cgt_user)
        await __fix_patient_users(wks, cgt, cgt_user)
        # await __fix_dashboard_users(wks, cgt, cgt_user)
