from core.logic import BaseCreate
from core.utils.strings import dict_w_camel_keys
from .mapper import Mapper
from ..model_db import DbHost
from ..model_web import DbHost as WebDbHost


class Create(BaseCreate):

    def __init__(self):
        super().__init__(DbHost, WebDbHost, Mapper())

    async def localhost(self):
        data = dict_w_camel_keys({
            "alias": "localhost",
            "name": "Local Tenant Host",
            "description": "",
            "connection_string_format": "mongodb://{host}/{dbname}",
            "db_host": "localhost",
            "db_user": "",
            "db_password": ""
        })
        web_object = WebDbHost(**data)
        await self.one(web_object)
