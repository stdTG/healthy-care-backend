from fastapi import Request
from mongoengine import Document

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from app.users.common.models.db import DashboardUser as DbDashboardUser
from app.users.dashboard.gql.utils import get_user_name
from core.sendbird.users import SendbirdUsers
from core.utils.aws import get_cognito_idp
from core.utils.transaction import Transaction


def rollback_delete_db_patient(db_object: Document):
    print("[DASHBOARD-USER-ROLLBACK] DB Patient")
    db_object.save()


def delete_db_patient(id_, trx):
    print("[DASHBOARD-USER-DELETE] DB Patient")

    db_object = DbDashboardUser.objects.with_id(id_)
    if not db_object:
        return

    db_object.deleted = True
    db_object.firstName = "Anonymous"
    db_object.lastName = db_object.role
    db_object.save()

    trx.push(rollback_delete_db_patient, db_object)

    return db_object


def disable_cognito_user(db_object, user_pool_id, trx):
    print("[DASHBOARD-USER-DELETE] Cognito Patient")
    username = get_user_name(db_object.email, db_object.phone)
    cognito_idp = get_cognito_idp()

    result = cognito_idp.admin_disable_user(UserPoolId=user_pool_id, Username=username)
    print("COGNITO User disabled")
    print(result)

    trx.push(rollback_disable_cognito_user, username, user_pool_id)
    return result


def rollback_disable_cognito_user(username, user_pool_id) -> None:
    cognito_idp = get_cognito_idp()
    cognito_idp.admin_enable_user(UserPoolId=user_pool_id, Username=username)


async def delete_user_handler(id_, request: Request):
    current_workspace: Workspace = await get_current_workspace(request)

    with Transaction("DashboardUserDelete") as trx:
        db_object: DbDashboardUser = delete_db_patient(id_, trx)
        if db_object:
            disable_cognito_user(db_object, current_workspace.cognito.user_pool_id,
                                 trx)

        users_client = SendbirdUsers(current_workspace.sendbird.app_id,
                                     current_workspace.sendbird.master_api_token)
        await users_client.delete(user_id=db_object.cognito_sub)

        trx.commitAll()

    return db_object
