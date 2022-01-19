from .auth_workspace import AuthWorkspace
from .jwks import JWKS


class AuthMetadata:

    def extract_jwks(self, workspace: AuthWorkspace) -> JWKS:
        region = workspace.aws_region
        user_pool_id = workspace.user_pool_id

        url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        jwks = JWKS.fromurl(url)
        return jwks
