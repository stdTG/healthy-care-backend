from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt
from jose.utils import base64url_decode
from starlette import status


class BaseTokenVerifier:

    def get_public_key(self, http_auth: HTTPAuthorizationCredentials, jwks_to_key: dict):
        token = http_auth.credentials
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authenticated"
            )

        public_key = jwks_to_key.get(kid)
        if not public_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="JWK public Attribute not found",
            )
        return public_key

    def verify_token(self, http_auth: HTTPAuthorizationCredentials, jwks_to_key: dict) -> bool:
        public_key = self.get_public_key(http_auth, jwks_to_key)
        if not public_key:
            # error handling is included in self.get_public_key
            return False

        message, encoded_sig = http_auth.credentials.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode())
        is_verified = public_key.verify(message.encode(), decoded_sig)

        print("[BaseTokenVerifier] Complete.")

        print("")
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not verified"
            )

        return is_verified
