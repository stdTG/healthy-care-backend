from web.cloudauth.auth_metadata import AuthMetadata
from web.cloudauth.auth_workspace import AuthWorkspace
from web.cloudauth.jwks import JWKS


def test_jwks_sample(aws_ctx):
    url = f"https://cognito-idp.{aws_ctx.region}.amazonaws.com/" \
          f"{aws_ctx.user_pool_id}/.well-known/jwks.json"
    jwks = JWKS.fromurl(url)
    print(jwks)


def test_auth_metadata(aws_ctx):
    auth_metadata = AuthMetadata()
    workspace = AuthWorkspace(region=aws_ctx.region, user_pool_id=aws_ctx.user_pool_id)
    jwks = auth_metadata.extract_jwks(workspace)
    print(jwks)
