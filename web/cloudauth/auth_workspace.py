from fastapi import HTTPException, Request
from starlette import status


class AuthWorkspace:

    def __init__(self, region: str, user_pool_id: str):
        self.aws_region = region
        self.user_pool_id = user_pool_id


def get_current_workspace_from_request(request: Request) -> AuthWorkspace:
    if not request:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current request is undefined",
        )

    if not hasattr(request.state, "current_workspace"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current request doesn't have 'current_workspace' set",
        )

    wks = request.state.current_workspace
    return AuthWorkspace(region=wks.aws_region, user_pool_id=wks.cognito.user_pool_id)
