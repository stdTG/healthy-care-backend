from app.tenant_workspaces.model_db import SystemUser, Workspace, WorkspaceSendbird
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

        sendbird: WorkspaceSendbird = obj.sendbird
        users_client = SendbirdUsers(sendbird.app_id, sendbird.master_api_token)

        full_name = f"system_user"

        sb_user = await users_client.create(user_id=cfg.SENDBIRD_SYSTEM_ACCOUNT,
                                            nickname=full_name, profile_url="",
                                            issue_access_token=True, issue_session_token=True)

        sendbird.system_user = SystemUser()
        sendbird.system_user.access_token = sb_user.data["access_token"]
        sendbird.system_user.user_id = cfg.SENDBIRD_SYSTEM_ACCOUNT
        sendbird.system_user.nickname = full_name

    return log
