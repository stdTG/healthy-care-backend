from typing import List

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from starlette import status


class AnonymousScopeVerifier:
    # this doesn't work yet. to let anonymous users just remove Demands/Auth dependency from route
    async def __call__(self) -> bool:
        return True


class ScopeVerifier:
    scope_key = "cognito:groups"

    def __init__(self, demanded_scopes: List[str]):
        self.demanded_scopes = demanded_scopes

    async def __call__(self, http_auth: HTTPAuthorizationCredentials) -> bool:

        print("[ScopeVerifier] Verifying...")
        self.claims = jwt.get_unverified_claims(http_auth.credentials)

        user_scopes = self.claims.get(self.scope_key)

        if user_scopes is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User doesn't have any roles assigned to him. {user_scopes}",
            )

        if "all_authenticated" in self.demanded_scopes:
            return True

        for demand in self.demanded_scopes:
            for uscope in user_scopes:
                # first match == authorization success
                if uscope == demand:
                    return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. None of {user_scopes} is allowed.",
        )
