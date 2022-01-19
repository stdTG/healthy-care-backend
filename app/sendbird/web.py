from datetime import datetime

from fastapi import Depends, Request

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace, WorkspaceSendbird
from core.sendbird.tokens import SendbirdTokens
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser
from .logic.dashboard_auth import sendbird_dashboard_user_auth_handler
from .logic.patient_auth import sendbird_patient_auth_handler
from .model_web import (SendbirdApiResponse, SendbirdUserOut, SendbirdSettingsOut,
                        SendbirdTokenOut,
                        SendbirdTokensOut)
from .router import router_normal, router_superadmin

get_current_user = AuthCurrentUser()


@router_normal.get("/sendbird/patient-user/auth", response_model=SendbirdUserOut)
async def sendbird_patient_auth(request: Request,
                                current_user: AuthClaims = Depends(get_current_user)):
    wks: Workspace = await get_current_workspace(request)
    return await sendbird_patient_auth_handler(wks, current_user)


@router_normal.get("/sendbird/dashboard-user/auth", response_model=SendbirdUserOut)
async def sendbird_dashboard_user_auth(request: Request,
                                       current_user: AuthClaims = Depends(get_current_user)):
    wks: Workspace = await get_current_workspace(request)
    return await sendbird_dashboard_user_auth_handler(wks, current_user)


@router_superadmin.get("/sendbird/settings-for-dashboard", response_model=SendbirdSettingsOut)
async def sendbird_get_settings_for_dashboard(request: Request):
    wks: Workspace = await get_current_workspace(request)
    return SendbirdSettingsOut(app_id=wks.sendbird.app_id, token=wks.sendbird.dashboard_token)


@router_superadmin.get("/sendbird/tokens", response_model=SendbirdTokensOut)
async def list_all_tokens(request: Request):
    wks: Workspace = await get_current_workspace(request)
    response = await SendbirdTokens(app_id=wks.sendbird.app_id,
                                    api_token=wks.sendbird.master_api_token) \
        .list_all(wks.sendbird.app_id)
    return SendbirdTokensOut(tokens=response.data["api_tokens"])


@router_superadmin.post("/sendbird/tokens", response_model=SendbirdApiResponse)
async def generate_token(request: Request):
    wks: Workspace = await get_current_workspace(request)
    response = await SendbirdTokens(app_id=wks.sendbird.app_id,
                                    api_token=wks.sendbird.master_api_token) \
        .generate(wks.sendbird.app_id)
    return SendbirdApiResponse(data=response.data)


@router_superadmin.post("/sendbird/tokens/regenerate-for-workspace",
                        response_model=SendbirdTokenOut)
async def regenerate_tokens_for_workspace(request: Request):
    wks: Workspace = await get_current_workspace(request)

    client = SendbirdTokens(app_id=wks.sendbird.app_id,
                            api_token=wks.sendbird.master_api_token)

    await client.revoke_all(wks.sendbird.app_id)
    sendbird: WorkspaceSendbird = wks.sendbird
    dashboard = await client.generate(wks.sendbird.app_id)

    sendbird.dashboard_token = dashboard.data["token"]
    sendbird.dashboard_token_created = datetime.fromtimestamp(
        dashboard.data["created_at"] / 1000
    ).strftime('%Y-%m-%d %H:%M:%S')
    wks.save()
    return SendbirdTokenOut(token=sendbird.dashboard_token,
                            created_at=sendbird.dashboard_token_created)


@router_superadmin.get("/sendbird/tokens/{api_token}", response_model=SendbirdTokenOut)
async def get_token_info(request: Request, api_token: str):
    wks: Workspace = await get_current_workspace(request)

    response = await SendbirdTokens(app_id=wks.sendbird.app_id,
                                    api_token=wks.sendbird.master_api_token).get_info(
        secondary_api_token=api_token, app_id=wks.sendbird.app_id)
    return SendbirdTokenOut(token=response.data["token"],
                            created_at=datetime.fromtimestamp(
                             response.data["created_at"] / 1000
                         ).strftime('%Y-%m-%d %H:%M:%S'))


@router_superadmin.delete("/sendbird/tokens/{api_token}", response_model=SendbirdApiResponse)
async def revoke_token(request: Request, api_token: str):
    wks: Workspace = await get_current_workspace(request)

    response = await SendbirdTokens(wks.sendbird.app_id, wks.sendbird.master_api_token) \
        .revoke(wks.sendbird.app_id, api_token)
    return SendbirdApiResponse(data=response.data)
