from app.tenant_workspaces.model_db import (Workspace as DbWorkspace,
                                            WorkspaceAwsCognito as DbWorkspaceAwsCognito)


async def run():
    log = []
    for obj in DbWorkspace.objects():
        wks: DbWorkspace = obj
        cgt: DbWorkspaceAwsCognito = wks.cognito
        if cgt.aws_region:
            continue
        log.append(cgt.user_pool_id)
        region = cgt.user_pool_id.split("_", 1)[0]
        log.append(region)
        cgt.aws_region = region
        wks.save()

    return log
