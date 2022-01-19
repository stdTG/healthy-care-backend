from app.tenant_db_hosts.logic import Create, Delete, Read, Update
from app.tenant_db_hosts.model_web import DbHost as WebDbHost
from app.tenant_db_hosts.web.router import router_superadmin_plural, router_superadmin_single
from web.core import ObjectIdStr


@router_superadmin_plural.get("/")
async def get_list():
    return await Read().list_all(map_2_web=True)


@router_superadmin_single.get("/{id}")
async def get_by_id(id: ObjectIdStr):
    return await Read().one_by_id(id, map_2_web=True)


@router_superadmin_single.post("/")
async def add(web_object: WebDbHost):
    return await Create().one(web_object, map_2_web=True)


@router_superadmin_single.post("/init")
async def init():
    return await Create().localhost()


@router_superadmin_single.put("/{id}")
async def update(web_object: WebDbHost):
    return await Update().one(web_object)


@router_superadmin_single.delete("/{id}")
async def delete(id: ObjectIdStr):
    return await Delete().one(id)
