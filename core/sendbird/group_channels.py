from core.sendbird.api_client import APIClient, ClientConfigCommon
from core.sendbird.base_module import BaseModule


class SendbirdGroupChannels(BaseModule):

    def __init__(self, app_id, master_token):
        api_client = APIClient(ClientConfigCommon(app_id, master_token))
        super().__init__(api_client, "group_channels", "channel_url")

    async def accept_invitation(self, **params):
        try:
            return await self.sb_api.request("put",
                                             f"{self.URL_MODULE}/{params.get(self.ID_PROP)}/accept",
                                             **params)
        except Exception as err:
            raise err
