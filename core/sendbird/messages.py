import asyncio

from core.sendbird.api_client import APIClient, ClientConfigCommon
from core.sendbird.base_module import BaseModule


class SendbirdMessages(BaseModule):

    def __init__(self, app_id, master_token, channel_url):
        api_client = APIClient(ClientConfigCommon(app_id, master_token))
        super().__init__(api_client, "group_channels/" + channel_url + "/messages", "")

    def send(self, message, sender_id: str = "783054", ):
        # sender_id should be bot`s id
        response = asyncio.run(self.create(message_type="MESG", message=message, user_id=sender_id))
        return response

    async def async_send(self, message, sender_id: str = "783054", ):
        # sender_id should be bot`s id
        response = await self.create(message_type="MESG", message=message, user_id=sender_id)
        return response
