from app.tenant_workspaces.model_db import (Workspace as DbWorkspace, WorkspaceSendbird)
from core.config import get_app_config
from core.sendbird.applications import Applications


async def run():
    cfg = get_app_config()
    log = [cfg.SENDBIRD_ORGANIZATION_API_TOKEN]

    for obj in DbWorkspace.objects().all():
        wks: DbWorkspace = obj
        try:
            application_service = Applications(cfg.SENDBIRD_ORGANIZATION_API_TOKEN)
            meta_info = await application_service.create(
                app_name=f"{cfg.ENVIRONMENT_NAME}-{wks.short_name}",
                region_key="frankfurt-1",
            )
            wks.sendbird = WorkspaceSendbird()
            wks.sendbird.app_id = meta_info.data["app_id"]
            wks.sendbird.app_name = meta_info.data["app_name"]
            wks.sendbird.master_api_token = meta_info.data["api_token"]
            wks.sendbird.master_api_token_created = meta_info.data["created_at"]
            wks.sendbird.region = meta_info.data["region"]["region_key"]
            wks.save()

            log.append(meta_info.data)
        except Exception as e:
            log.append(e)

    return log
