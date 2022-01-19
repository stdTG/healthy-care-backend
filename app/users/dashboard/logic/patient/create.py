from fastapi import Request

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace, WorkspaceSendbird
from app.user_roles import Roles
from app.users.common.models.db import PatientUser as DbPatientUser, SendbirdSettings
from app.users.dashboard.gql.inputs import PatientUserInput
from app.users.dashboard.gql.utils import get_user_name, is_empty, set_verification_tokens
from app.users.dashboard.logic.verification_helper import (EmailHelper, PhoneHelper,
                                                           VerificationHelper)
from core.cognito import CognitoUsers
from core.sendbird.group_channels import SendbirdGroupChannels
from core.sendbird.users import SendbirdUsers
from core.utils.aws import get_cognito_idp
from core.utils.random import Random
from core.utils.transaction import Transaction
from core.utils.transaction_async import TransactionAsync


async def rollback_db_patient(db_object: DbPatientUser):
    print("[PATIENT-ROLLBACK] DB Patient")
    db_object.delete()


def create_db_patient(web_object: PatientUserInput, trx: Transaction):
    print("[PATIENT-CREATE] DB Patient")

    db_object = DbPatientUser.from_gql(web_object)
    db_object.save()

    print("DB Patient Created")
    print(db_object)

    trx.push(rollback_db_patient, db_object)
    return db_object


async def rollback_create_cognito_user(username: str, user_pool_id: str):
    print(f"[PATIENT-ROLLBACK] Cognito Patient deleting {username} "
          f"| {user_pool_id}")
    cognito_idp = get_cognito_idp()
    response = cognito_idp.admin_delete_user(
        UserPoolId=user_pool_id,
        Username=username
    )
    print(response)


def create_cognito_user(web_object: PatientUserInput, user_pool_id: str, trx: Transaction):
    print("[PATIENT-CREATE] Cognito Patient")
    username = get_user_name(web_object.email, web_object.phone)
    cognito_idp = get_cognito_idp()
    result = cognito_idp.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        ForceAliasCreation=False,
        MessageAction="SUPPRESS",
        TemporaryPassword=web_object.password,
    )
    print("COGNITO User created")
    print(result)

    trx.push(rollback_create_cognito_user, username, user_pool_id)
    return result


async def create_patient_handler(web_object: PatientUserInput,
                                 request: Request) -> DbPatientUser:
    """
    1. Create Patient record in DB
    2. Create Cognito record
    3. Generate VerificationCode and verificationToken and save in DB
    """

    if web_object.byEmail:
        web_object.email = web_object.byEmail.email.lower().strip()

    if web_object.byPhone:
        web_object.phone = web_object.byPhone.phone.lower().strip()

    if not hasattr(web_object, 'password') or is_empty(web_object.password):
        web_object.password = Random.password()

    current_workspace: Workspace = await get_current_workspace(request)
    cognito_users = CognitoUsers(aws_region=current_workspace.aws_region)

    async with TransactionAsync("PatientCreate") as trx:
        db_object = create_db_patient(web_object, trx)
        cognito_object = create_cognito_user(web_object, current_workspace.cognito.user_pool_id,
                                             trx)

        username = get_user_name(web_object.email, web_object.phone)
        cognito_users.add_to_group(current_workspace.cognito.user_pool_id, username, Roles.PATIENT)

        print("Updating DB.cognito_sub")
        user_sub = cognito_object["User"]["Username"]
        db_object.cognito_sub = user_sub

        print("Sendbird: User & GroupChannel")
        await create_sendbird_user(db_object, current_workspace, trx=trx)
        db_object.save()

        tokens = set_verification_tokens(db_object.id, web_object.email, web_object.phone, trx)
        if web_object.byEmail and web_object.byEmail.sendEmail:
            verification = tokens["email"]
            helper = EmailHelper()
            __send_invite_message(helper, verification.username, "Welcome message. Link to app")

        if web_object.byPhone and web_object.byPhone.sendSms:
            verification = tokens["phone"]
            helper = PhoneHelper()
            __send_invite_message(helper, verification.username, "Welcome message. Link to app")

        trx.commitAll()

    return db_object


def __send_invite_message(helper: VerificationHelper, username: str, message: str):
    params = {
        "message_html": f"<html><body>{message}</body></html>",
        "subject_title": "Alakine mobile app",
        "message_text": message,
        "username": username,
    }
    helper.send_code_to_user(**params)


async def create_sendbird_user(db_object: DbPatientUser, workspace: Workspace, trx: Transaction):
    """Sendbird stuff"""

    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)
    gchannels_client = SendbirdGroupChannels(sendbird.app_id, sendbird.master_api_token)

    full_name = f"{db_object.firstName} {db_object.lastName}".rstrip()
    sendbird_feed_channel_url = f"feed-{db_object.cognito_sub}"

    trx.push(rollback_create_sendbird_user, workspace=workspace, user_id=db_object.cognito_sub,
             channel_url=sendbird_feed_channel_url)

    sb_user = await users_client.create(user_id=db_object.cognito_sub,
                                        nickname=full_name, profile_url="",
                                        issue_access_token=True, issue_session_token=True)
    sb_channel = await gchannels_client.create(name=f"feed-{full_name}",
                                               channel_url=sendbird_feed_channel_url,
                                               user_ids=[db_object.cognito_sub])
    print("Sendbird: user")
    print(sb_user.data)
    print("Sendbird: sb_channel")
    print(sb_channel.data)

    db_object.sendbird = SendbirdSettings()
    db_object.sendbird.feed_channel_url = sendbird_feed_channel_url
    db_object.sendbird.access_token = sb_user.data["access_token"]
    db_object.sendbird.session_tokens = sb_user.data["session_tokens"]


async def rollback_create_sendbird_user(workspace, user_id, channel_url):
    print("[ROLLBACK-patient] creating sendbird user")
    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)
    gchannels_client = SendbirdGroupChannels(sendbird.app_id, sendbird.master_api_token)

    await users_client.delete(user_id=user_id)
    await gchannels_client.delete(channel_url=channel_url, )
