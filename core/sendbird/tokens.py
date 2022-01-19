from core.sendbird.api_client import APIClient, ClientConfigCommon
from core.sendbird.sendbird_response import SendbirdResponse

URL_GENERATE = "applications/api_tokens"
URL_LIST = "applications/api_tokens"
URL_GET_INFO = "applications/api_tokens/{secondary_api_token}"
URL_REVOKE = "applications/api_tokens/{secondary_api_token}"


class SendbirdTokens:

    def __init__(self, app_id: str, api_token: str):
        self.sb_api = APIClient(ClientConfigCommon(app_id, api_token))

    async def generate(self, app_id: str):
        try:
            return await self.sb_api.request("post", URL_GENERATE, app_id=app_id)
        except Exception as err:
            raise err

    async def list_all(self, app_id: str) -> SendbirdResponse:
        try:
            return await self.sb_api.request("get", URL_LIST, app_id=app_id)
        except Exception as err:
            raise err

    async def get_info(self, app_id: str, secondary_api_token: str):
        url = URL_GET_INFO.format(secondary_api_token=secondary_api_token)
        try:
            return await self.sb_api.request("get", url, app_id=app_id,
                                             secondary_api_token=secondary_api_token)
        except Exception as err:
            raise err

    async def revoke(self, app_id: str, secondary_api_token: str):
        url = URL_REVOKE.format(secondary_api_token=secondary_api_token)
        try:
            return await self.sb_api.request("delete", url, app_id=app_id,
                                             )
        except Exception as err:
            raise err

    async def revoke_all(self, app_id: str) -> bool:
        try:
            tokens = await self.list_all(app_id)

            for t in tokens.data["api_tokens"]:
                await self.revoke(app_id, t["token"])
            return True
        except Exception as err:
            raise err
