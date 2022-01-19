from core.sendbird.api_client import APIClient, ClientConfigCommon
from core.sendbird.base_module import BaseModule


class SendbirdUsers(BaseModule):

    def __init__(self, app_id, api_token):
        api_client = APIClient(ClientConfigCommon(app_id, api_token))
        super().__init__(api_client, "users", "user_id")

