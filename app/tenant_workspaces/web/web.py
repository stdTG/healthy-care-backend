import sys
import traceback

from fastapi import Request, status
from mongoengine import NotUniqueError

from app.context import get_current_workspace, get_public_workspace_by_short_name
from app.tenant_db_hosts.model_db import DbHost
from core.errors import HTTPNotFoundError
from web.core.results import ErrorResponse
from .router import (router_common_single, router_init_master, router_public_single,
                     router_superadmin_plural)
from ..logic import Create as WorkspaceFactory, DropWorkspace
from ..model_db import Workspace
from ..model_web import Workspace as WebWorkspace, WorkspacePublicOut


def get_hosts(web_workspace: WebWorkspace):
    host_data = {
        "alias": web_workspace.dbHosts.hostAlias1,
        "name": f"{web_workspace.shortName}_1",
        "description": "",
        "db_host": "localhost",
        "db_user": "",
        "db_password": ""
    }
    return DbHost(**host_data)


@router_public_single.get("/{short_name}", response_model=WorkspacePublicOut, responses={
    404: {"model": ErrorResponse,
          "description": "The workspace not found"}, })
async def get_public_by_short_name(short_name: str):
    wks: Workspace = get_public_workspace_by_short_name(short_name)
    if not wks:
        raise HTTPNotFoundError(f"Workspace {short_name} not found")

    return {**wks.to_mongo(), **wks.cognito.to_mongo()}


@router_common_single.get("/current")
async def get_current_workspace_api(request: Request):
    wks = await get_current_workspace(request)
    return {
        "shortName": wks.short_name,
        "fullName": wks.human_friendly_name
    }


@router_superadmin_plural.get("/")
async def get_list():
    result = []

    for wks in Workspace.objects:
        result.append({"shortName": wks.short_name,
                       "fullName": wks.human_friendly_name,
                       "admin": {
                           "email": wks.admin_email,
                           "phone": wks.admin_phone_number,
                       },
                       "cognito": {
                           "awsRegion": wks.aws_region,
                           "userPoolId": wks.cognito.user_pool_id,
                           "clientId": wks.cognito.dashboard_client_id,
                           "dashboardClientId": wks.cognito.dashboard_client_id,
                           "mobileClientId": wks.cognito.mobile_client_id
                       }})

    return result


@router_init_master.post("/init-master-workspace",
                         responses={409: {"model": ErrorResponse,
                                          "description": "The workspace already exists"},
                                    200: {"description": "Master workspace was created"},
                                    }
                         )
async def add(web_workspace: WebWorkspace):
    if WorkspaceFactory.exists(web_workspace.shortName) or WorkspaceFactory.exists("ignilife"):
        return ErrorResponse.create_response(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Workspace with provided [{web_workspace.shortName}] already exists",
        )

    try:
        get_hosts(web_workspace).save()
    except NotUniqueError:
        print("Db host with provided db alias already exists")

    try:
        workspace_factory = WorkspaceFactory(web_workspace, make_super_admin=True)
        _ = await workspace_factory.master()
        return {}
    except Exception as e:
        # if exception will raised in middleware, when will create database
        traceback.print_exc(file=sys.stdout)
        return ErrorResponse.create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Server error",
        )


@router_superadmin_plural.post("/", responses={409: {"model": ErrorResponse,
                                                     "description": "The workspace already exists"},
                                               200: {"description": "Master workspace was created"},
                                               500: {"model": ErrorResponse,
                                                     "description": "Server error"},
                                               }
                               )
async def add_wp(web_workspace: WebWorkspace):
    if WorkspaceFactory.exists(web_workspace.shortName):
        return ErrorResponse.create_response(
            status_code=status.HTTP_409_CONFLICT,
            message=f"Workspace with provided [{web_workspace.shortName}] already exists",
        )

    workspace_factory = WorkspaceFactory(web_workspace)
    _ = await workspace_factory.tenant()
    return {}


@router_superadmin_plural.delete("/{short_name}",
                                 responses={
                                     200: {"description": "Master workspace was created"},
                                 })
async def delete(short_name: str):
    await DropWorkspace().execute(short_name)
    return {}


@router_superadmin_plural.get("/{short_name}")
async def get_by_short_name(short_name: str):
    wks: Workspace = get_public_workspace_by_short_name(short_name)
    if not wks:
        raise HTTPNotFoundError(f"Workspace {short_name} not found")

    return {
        "shortName": wks.short_name,
        "fullName": wks.human_friendly_name,
        "admin": {
            "email": wks.admin_email,
            "phone": wks.admin_phone_number,
        },
        "cognito": {
            "awsRegion": wks.aws_region,
            "userPoolId": wks.cognito.user_pool_id,
            "clientId": wks.cognito.dashboard_client_id,
            "dashboardClientId": wks.cognito.dashboard_client_id,
            "mobileClientId": wks.cognito.mobile_client_id
        }
    }
