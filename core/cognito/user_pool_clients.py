from core.config import get_app_config
from core.utils.aws import get_cognito_idp


class CognitoUserPoolClients:

    def __init__(self, aws_region: str = "eu-west-1"):
        # cfg = get_app_config()
        self.client = get_cognito_idp(aws_region)

    def create(self, user_pool_id, app_client_name):
        response = self.client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=app_client_name,
            GenerateSecret=False,
            RefreshTokenValidity=30,
            # AccessTokenValidity = 123,
            # IdTokenValidity = 123,
            # DefaultRedirectURI = '',
            PreventUserExistenceErrors='ENABLED'
        )
        return response["UserPoolClient"]["ClientId"]
