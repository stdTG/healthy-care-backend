from typing import List

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth_metadata import AuthMetadata
from .scope_verifier import ScopeVerifier
from .token_verifier import TokenVerifier


class Authorization:

    # allowed values besides cognito groups are: ["any_authenticated"]
    def allow(self, roles: List[str], target: str = "UnknownTarget"):
        print(f"[APP-AUTH] {target} | {roles}")

        return Authorizer(TokenVerifier(), ScopeVerifier(roles))


class Authorizer:

    def __init__(self, token_verifier: TokenVerifier, scope_verifier: ScopeVerifier):
        self.token_verifier = token_verifier
        self.scope_verifier = scope_verifier

    async def __call__(
            self,
            request: Request,
            http_auth: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
            auth_metadata: AuthMetadata = Depends(),
    ):
        print("[AUTHORIZER] Authorization...")

        await self.token_verifier(request, http_auth, auth_metadata)

        await self.scope_verifier(http_auth)
