from __future__ import annotations

import collections
from typing import TYPE_CHECKING

from aiodataloader import DataLoader
from graphql.execution.utils import collect_fields

from app.users.common.models.db import DashboardUser as User

if TYPE_CHECKING:
    from app.tenant_workspaces.model_db import Workspace

from fastapi import Request

from core.errors import HTTPException, HTTPNotFoundError
from app.org_units.model_db import OrgUnit

from app.tenant_db_hosts.model_db import DbHost
from app.tenant_workspaces.model_db import Workspace


def get_public_workspace_by_short_name(short_name: str) -> Workspace:
    db_object: Workspace = Workspace.objects(short_name=short_name.lower()).first()
    return db_object


async def init_current_workspace(request: Request):
    if hasattr(request.state, "current_workspace"):
        return

    request.state.current_workspace = None

    if not request:
        raise Exception("To initialize current workspace you need to provide current Request")

    wks_name = request.headers.get("Workspace", None)
    # wks_name = "ignilife"

    if not wks_name:
        print("Workspace name has not been provided. Skipping...")
        return

    print("[WORKSPACE] Getting workspace data: %s" % wks_name)
    wks = Workspace.objects(short_name=wks_name.lower()).first()
    if not wks:
        raise HTTPNotFoundError("Workspace couldn't be initialized")
    db_host_1: DbHost = DbHost.objects(alias=wks.tenant_db_1.host_alias).first()
    db_host_2: DbHost = DbHost.objects(alias=wks.tenant_db_2.host_alias).first()

    print(f"[WORKSPACE] Tenant: {wks.human_friendly_name}")
    print(f"[WORKSPACE] Tenant AWS Region: {wks.aws_region}")
    print(f"[WORKSPACE] Tenant AWS Cognito: {wks.cognito.user_pool_id}")

    print(f"[WORKSPACE] Tenant HOST 1: {db_host_1.db_host}")
    print(f"[WORKSPACE] Tenant DB 1: {wks.tenant_db_1.db_name}")

    print(f"[WORKSPACE] Tenant HOST 2: {db_host_2.db_host}")
    print(f"[WORKSPACE] Tenant DB 2: {wks.tenant_db_2.db_name}")

    if not wks:
        raise Exception("Workspace couldn't be initialized")

    request.state.current_workspace = wks


async def get_current_workspace(request: Request) -> Workspace:
    if hasattr(request.state, "current_workspace"):
        return request.state.current_workspace

    raise HTTPException(status_code=400, detail="Workspace header invalid")


async def get_current_master_org(request: Request) -> OrgUnit:
    workspace = await get_current_workspace(request)

    return OrgUnit.objects.filter(name=workspace.human_friendly_name).first()


async def get_current_auth(request: Request):
    return request.state.auth_claims


async def get_user(info) -> User:
    request = info.context["request"]
    auth = await get_current_auth(request)
    return User.objects(cognito_sub=auth.sub).first()


async def get_loader(info, name: str) -> DataLoader:
    return info.context.get('request').state._state.get("loaders").get(name)


def get_fields(info):
    """Return requested fields"""
    prev_fragment_names = set()
    params = collections.defaultdict(list)
    params = collect_fields(info.context,
                            info.parent_type,
                            info.field_asts[0].selection_set,
                            params,
                            prev_fragment_names)

    for fragment_name in prev_fragment_names:
        params = collect_fields(info.context,
                                info.parent_type,
                                info.fragments[fragment_name].selection_set,
                                params,
                                prev_fragment_names)

    return list(params.keys())
