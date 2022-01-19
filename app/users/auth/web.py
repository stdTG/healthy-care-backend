from fastapi import Depends, Form, Request, status
from pycognito.exceptions import ForceChangePasswordException

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from app.users.dashboard.logic.verification_helper import EmailHelper, PhoneHelper
from core.cognito import CognitoUsers, authentication
from core.errors import HTTPNotFoundError
from web.core.results import ErrorResponse
from web.core.tenants import workspace_header
from .logic.create_password import create_password_handler
from .logic.reset_password import reset_password_handler
from .logic.verify_code import verify_code_handler
from .logic.verify_username import verify_username_handler
from .router import router_mobile_auth_public, router_public
from .web_model import (MobileAuthCreatePasswordIn, MobileAuthCreatePasswordOut,
                        MobileAuthVerifyCode, MobileAuthVerifyCodeOut, MobileAuthVerifyUsernameIn,
                        MobileAuthVerifyUsernameOut, SignInResponse, UserInfoResult)
from ..common.models.db import DashboardUser


@router_mobile_auth_public.post("/verify-email", response_model=MobileAuthVerifyUsernameOut)
async def verify_email(data: MobileAuthVerifyUsernameIn,
                       request: Request) -> MobileAuthVerifyUsernameOut:
    """Send 4 numbers code to user.
    Parameter 'reset' generated new 4 numbers code"""
    return await verify_username_handler(data, EmailHelper(), request)


@router_mobile_auth_public.post("/verify-phone", response_model=MobileAuthVerifyUsernameOut)
async def verify_phone(data: MobileAuthVerifyUsernameIn,
                       request: Request) -> MobileAuthVerifyUsernameOut:
    return await verify_username_handler(data, PhoneHelper(), request)


@router_mobile_auth_public.post("/verify-code", response_model=MobileAuthVerifyCodeOut,
                                dependencies=[Depends(workspace_header)])
async def verify_code(data: MobileAuthVerifyCode, request: Request):
    return await verify_code_handler(data, request)


@router_mobile_auth_public.post("/create-password", response_model=MobileAuthCreatePasswordOut,
                                response_description="message with code sended",
                                dependencies=[Depends(workspace_header)])
async def create_password(data: MobileAuthCreatePasswordIn, request: Request):
    """
    Default Password Policy:
        - 8 symbols
        - [a-z]
        - [A-Z]
    """
    return {"credential_status": await create_password_handler(data, request)}


@router_public.post("/auth/sign-in", response_model=SignInResponse, responses={
    401: {"model": ErrorResponse,
          "description": "Change password before authenticating"},
    403: {"model": ErrorResponse,
          "description": "Incorrect username / password"},
    500: {"model": ErrorResponse,
          "description": "Server error. Error sign-in "},
})
async def sign_in(request: Request, username: str = Form(...), password: str = Form(...)):
    wks: Workspace = await get_current_workspace(request)
    try:
        result = await authentication.sign_in_jwt(
            wks.cognito.user_pool_id,
            wks.cognito.dashboard_client_id,
            username,
            password
        )
        return result
    except ForceChangePasswordException as err:
        return ErrorResponse.create_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=f"Change password before authenticating"
        )
    except Exception as err:
        if err.response["Error"]["Code"] == "NotAuthorizedException":
            return ErrorResponse.create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message=err.response["Error"]["Message"]
            )
        else:
            raise


@router_public.post("/auth/reset-password", response_model=MobileAuthVerifyUsernameOut,
                    responses={
                        404: {"model": ErrorResponse,
                              "description": "User not found"}, }
                    )
async def reset_password(request: Request, username: str = Form(...)):
    user = DashboardUser.objects.filter(email=username, deleted=False).first()
    username = username.strip()
    if user:
        type_ = "email"
        helper = EmailHelper()
    else:
        user = DashboardUser.objects.filter(phone=username, deleted=False).first()
        type_ = "phone"
        helper = PhoneHelper()

    if not user:
        raise HTTPNotFoundError(f"User not found `{username}`")

    return await reset_password_handler(username, user.id, type_, helper)


@router_public.get("/auth/user-info/{username}", response_model=UserInfoResult)
async def get_user_info(request: Request, username: str):
    wks: Workspace = await get_current_workspace(request)
    cgt_user = CognitoUsers().get_user(wks.cognito.user_pool_id, username)
    return UserInfoResult(**cgt_user._asdict())
