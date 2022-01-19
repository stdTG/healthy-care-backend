from __future__ import annotations

from typing import TYPE_CHECKING, Union

from app.tenant_workspaces.model_db import Workspace, WorkspaceSendbird
from app.users.dashboard.gql.utils import get_user_name, is_empty, set_verification_tokens
from app.users.dashboard.logic.verification_helper import (EmailHelper, PhoneHelper,
                                                           VerificationHelper)
from core.sendbird.users import SendbirdUsers
from core.utils.aws import get_cognito_idp
from core.utils.random import Random
from core.utils.transaction import Transaction
from core.utils.transaction_async import TransactionAsync

if TYPE_CHECKING:
    from app.users.dashboard.gql.inputs import DashboardUserInput

from app.users.common.models.db import (DashboardUser as DbDashboardUser, CognitoUser,
                                        SendbirdSettings)
from core.cognito import CognitoUsers


async def rollback_db_dashboard_user(db_object: DbDashboardUser):
    print("[DASHBOARD-USER-ROLLBACK] DB Dashboard user")
    db_object.delete()


def create_db_dashboard_user(web_object: Union[DashboardUserInput, CognitoUser], trx: Transaction):
    print("[DASHBOARD-USER-ROLLBACK] DB Dashboard user")

    db_object = DbDashboardUser.from_gql(web_object)
    db_object.save()

    print("DB Dashboard user")
    print(db_object)

    trx.push(rollback_db_dashboard_user, db_object)
    return db_object


async def rollback_create_cognito_user(username: str, user_pool_id: str):
    print(f"[DASHBOARD-USER-ROLLBACK] Cognito Dashboard user deleting {username} | {user_pool_id}")
    cognito_idp = get_cognito_idp()
    response = cognito_idp.admin_delete_user(
        UserPoolId=user_pool_id,
        Username=username
    )
    print(response)


def create_cognito_user(cognito_users, web_object: Union[DashboardUserInput, CognitoUser],
                        user_pool_id: str,
                        trx: Transaction):
    print("[DASHBOARD-USER-CREATE] Cognito Dashboard user")
    username = get_user_name(web_object.email, web_object.phone)
    cognito_idp = get_cognito_idp()
    is_activate_pass = False

    if not hasattr(web_object, "password") or is_empty(web_object.password):
        web_object.password = Random.password()
    else:
        is_activate_pass = True

    result = cognito_idp.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        ForceAliasCreation=False,
        MessageAction="SUPPRESS",
        TemporaryPassword=web_object.password,
    )

    if is_activate_pass:
        cognito_users.set_password(user_pool_id, username, web_object.password)
        print("Password was settled")

    print("COGNITO User created")
    print(result)

    trx.push(rollback_create_cognito_user, username, user_pool_id)
    return result


async def create_dashboard_user_handler(web_object: Union[DashboardUserInput, CognitoUser],
                                        current_workspace: Workspace) -> DbDashboardUser:
    """
    1. Create Dashboard user record in DB
    2. Create Cognito record
    3. Generate VerificationCode and verificationToken and save in DB
    """

    if isinstance(web_object, DbDashboardUser):
        if web_object.email:
            web_object.email = web_object.email.lower().strip()

        if web_object.phone:
            web_object.phone = web_object.phone.lower().strip()

    cognito_users = CognitoUsers(aws_region=current_workspace.aws_region)

    async with TransactionAsync("DashboardUserCreate") as trx:
        db_object = create_db_dashboard_user(web_object, trx)
        cognito_object = create_cognito_user(
            cognito_users,
            web_object,
            current_workspace.cognito.user_pool_id,
            trx
        )

        username = get_user_name(web_object.email, web_object.phone)
        cognito_users.add_to_group(current_workspace.cognito.user_pool_id, username,
                                   web_object.role)

        print("Updating DB.cognito_sub")
        db_object.cognito_sub = cognito_object["User"]["Username"]

        await create_sendbird_user(db_object, current_workspace, trx=trx)
        db_object.save()

        tokens = set_verification_tokens(db_object.id, web_object.email, web_object.phone, trx)

        if web_object.byEmail and web_object.byEmail.sendEmail:
            verification = tokens["email"]
            helper = EmailHelper()
            __send_temp_pass_to_user(helper, verification.username, web_object.password)

        if web_object.byPhone and web_object.byPhone.sendSms:
            verification = tokens["phone"]
            helper = PhoneHelper()
            __send_temp_pass_to_user(helper, verification.username, web_object.password)

        trx.commitAll()

    return db_object


def __send_temp_pass_to_user(helper: VerificationHelper, username: str, password: str):
    params = {
        "message_html": f"<html><body>Your temporary password is:"
                        f" <strong>{password}</strong> </body></html>",
        "subject_title": "Alakine Temporary password",
        "message_text": f"Your temporary password is: {password}",
        "username": username,
    }
    helper.send_code_to_user(**params)


async def create_sendbird_user(db_object: DbDashboardUser, workspace: Workspace, trx: Transaction):
    """Sendbird stuff"""

    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)

    full_name = f"{db_object.firstName} {db_object.lastName}".rstrip()

    trx.push(rollback_create_sendbird_user, workspace=workspace, user_id=db_object.cognito_sub, )
    sb_user = await users_client.create(user_id=db_object.cognito_sub,
                                        nickname=full_name, profile_url="",
                                        issue_access_token=True, issue_session_token=True)
    print("Sendbird: user")
    print(sb_user.data)

    db_object.sendbird = SendbirdSettings()
    db_object.sendbird.access_token = sb_user.data["access_token"]
    db_object.sendbird.session_tokens = sb_user.data["session_tokens"]


async def rollback_create_sendbird_user(workspace, user_id):
    print("[ROLLBACK-user] creating sendbird user")
    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)

    await users_client.delete(user_id=user_id)
