from fastapi import Request

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from core.config import get_app_config
from core.utils.db import register_master_connection, register_tenant_connection


async def init_master_db():
    print("[MASTER-DB] Initialization")
    cfg = get_app_config()
    register_master_connection(cfg)
    print("[MASTER-DB] Done")


async def init_tenant_db(request: Request):
    print("[TENANT-DB] Initialization")
    wks: Workspace = await get_current_workspace(request)
    if wks is None:
        print("[TENANT-DB] Skipped")
        return
    await register_tenant_dbs(wks)


async def register_tenant_dbs(wks: Workspace):
    cfg = get_app_config()
    await register_tenant_connection(cfg, wks.tenant_db_1, "tenant-db-basic-data")
    await register_tenant_connection(cfg, wks.tenant_db_2, "tenant-db-personal-data")
    print(f"[TENANT-DB] Registered for [{wks.short_name}]")
