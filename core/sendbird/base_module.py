from __future__ import annotations
from typing import TYPE_CHECKING

from core.sendbird.sendbird_response import SendbirdResponse

if TYPE_CHECKING:
    from core.sendbird.api_client import APIClient


class BaseModule:

    def __init__(self, client: APIClient, url_module, id_prop):
        self.sb_api = client
        self.URL_MODULE = url_module
        self.ID_PROP = id_prop

    async def create(self, **params) -> SendbirdResponse:
        try:
            return await self.sb_api.request("post", f"{self.URL_MODULE}", **params)
        except Exception as err:
            raise err

    async def list(self, **params) -> SendbirdResponse:
        try:
            return await self.sb_api.request("get", self.URL_MODULE, **params)
        except Exception as err:
            raise err

    async def read(self, **params) -> SendbirdResponse:
        try:
            return await self.sb_api.request("get", f"{self.URL_MODULE}/{params.get(self.ID_PROP)}",
                                             **params)
        except Exception as err:
            raise err

    async def update(self, **params) -> SendbirdResponse:
        try:
            return await self.sb_api.request("put", f"{self.URL_MODULE}/{params.get(self.ID_PROP)}",
                                             **params)
        except Exception as err:
            raise err

    async def delete(self, **params) -> SendbirdResponse:
        try:
            return await self.sb_api.request("delete",
                                             f"{self.URL_MODULE}/{params.get(self.ID_PROP)}",
                                             **params)
        except Exception as err:
            raise err
