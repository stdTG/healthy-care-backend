from app.tenant_workspaces.model_db import Workspace, WorkspaceSendbird
from app.users.common.models.db import PatientUser, DashboardUser, SendbirdSettings

from core.config import get_app_config
from core.sendbird.group_channels import SendbirdGroupChannels
from core.sendbird.users import SendbirdUsers
from web.startup.db_and_tenant import register_tenant_dbs


async def run():
    cfg = get_app_config()
    log = []

    for obj in Workspace.objects():
        wks: Workspace = obj
        await register_tenant_dbs(wks)

        for patient in PatientUser.objects().all():
            try:
                await create_sendbird_patient(patient, workspace=wks, )
                patient.save()
            except Exception as e:
                print(e)
                log.append(e)

        for user in DashboardUser.objects().all():
            try:
                await create_sendbird_user(user, workspace=wks, )
                user.save()
            except Exception as e:
                print(e)
                log.append(e)

    return log


async def create_sendbird_patient(db_object: PatientUser, workspace: Workspace,):
    """Sendbird stuff"""

    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)
    gchannels_client = SendbirdGroupChannels(sendbird.app_id, sendbird.master_api_token)

    full_name = f"{db_object.firstName} {db_object.lastName}".rstrip()
    sendbird_feed_channel_url = f"feed-{db_object.cognito_sub}"

    sb_user = await users_client.create(user_id=db_object.cognito_sub,
                                        nickname=full_name, profile_url="",
                                        issue_access_token=True, issue_session_token=True)
    sb_channel = await gchannels_client.create(name=f"feed-{full_name}",
                                               channel_url=sendbird_feed_channel_url,
                                               user_ids=[db_object.cognito_sub])

    db_object.sendbird = SendbirdSettings()
    db_object.sendbird.feed_channel_url = sendbird_feed_channel_url
    db_object.sendbird.access_token = sb_user.data["access_token"]
    db_object.sendbird.session_tokens = sb_user.data["session_tokens"]


async def create_sendbird_user(db_object: DashboardUser, workspace: Workspace):
    """Sendbird stuff"""

    sendbird: WorkspaceSendbird = workspace.sendbird
    users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)

    full_name = f"{db_object.firstName} {db_object.lastName}".rstrip()

    sb_user = await users_client.create(user_id=db_object.cognito_sub,
                                        nickname=full_name, profile_url="",
                                        issue_access_token=True, issue_session_token=True)

    db_object.sendbird = SendbirdSettings()
    db_object.sendbird.access_token = sb_user.data["access_token"]
    db_object.sendbird.session_tokens = sb_user.data["session_tokens"]


