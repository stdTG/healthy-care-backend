from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwk

from .auth_metadata import AuthMetadata
from .auth_workspace import get_current_workspace_from_request
from .base_token_verifier import BaseTokenVerifier


class TokenVerifier(BaseTokenVerifier):
    """
    Verify `Access token` and authorize it based on scope (or groups)
    """

    async def __call__(
            self,
            request: Request,
            http_auth: HTTPAuthorizationCredentials,
            auth_metadata: AuthMetadata,
            auto_error: bool = True,
    ) -> bool:
        print("[TokenVerifier] Verifying...")

        wks = get_current_workspace_from_request(request)
        jwks = auth_metadata.extract_jwks(wks)
        jwks_to_key = {_jwk["kid"]: jwk.construct(_jwk) for _jwk in jwks.keys}

        return self.verify_token(http_auth, jwks_to_key)
