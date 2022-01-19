from core.sendbird.api_client import APIClient, ClientConfigApplications
from core.sendbird.base_module import BaseModule


class Applications(BaseModule):
    """
    region_key:
        frankfurt-1
        mumbai-1
        north-virginia-2
        oregon-1
    """

    def __init__(self, organization_api_key):
        api_client = APIClient(ClientConfigApplications(organization_api_key))
        super().__init__(api_client, "applications", "app_id")

    async def push_notification(self, **params):
        try:
            return await self.sb_api.request(
                "patch",
                f"{self.URL_MODULE}/{params.get(self.ID_PROP)}/push_notification",
                **params)
        except Exception as err:
            raise err

    async def copy_settings_to(self, **params):
        try:
            return await self.sb_api.request(
                "put",
                f"{self.URL_MODULE}/{params.get(self.ID_PROP)}/copy_settings_to",
                **params)
        except Exception as err:
            raise err
