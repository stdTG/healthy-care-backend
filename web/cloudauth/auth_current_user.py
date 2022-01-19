from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwk, jwt
from pydantic import ValidationError
from starlette import status

from .auth_claims import AuthClaims
from .auth_metadata import AuthMetadata
from .auth_workspace import get_current_workspace_from_request
from .base_token_verifier import BaseTokenVerifier


class AuthCurrentUser(BaseTokenVerifier):

    async def __call__(
            self,
            request: Request,
            http_auth: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
            auth_metadata: AuthMetadata = Depends(),
    ) -> Optional[AuthClaims]:

        wks = get_current_workspace_from_request(request)
        jwks = auth_metadata.extract_jwks(wks)
        jwks_to_key = {_jwk["kid"]: jwk.construct(_jwk) for _jwk in jwks.keys}

        is_verified = self.verify_token(http_auth, jwks_to_key)
        if not is_verified:
            return None

        claims = jwt.get_unverified_claims(http_auth.credentials)
        print(claims)

        try:
            user: AuthClaims = AuthClaims.parse_obj(claims)
            user.roles = claims["cognito:groups"]
            return user
        except ValidationError as err:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Validation Error for Claims. " + str(err),
            )
