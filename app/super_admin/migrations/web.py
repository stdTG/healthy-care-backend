from fastapi import Form

from .migrations_logic import MigrationsLogic
from .router import router_superadmin


@router_superadmin.get("/migrations/list")
async def migrations_list():
    return await MigrationsLogic().list_all()


@router_superadmin.post("/migration/execute")
async def migration_execute(migration_name: str = Form(...)):
    return await MigrationsLogic().execute(migration_name)
