from bson import SON

from core.logic import BaseMapper
from ..model_db import DbHost
from ..model_web import DbHost as WebDbHost

ATLAS_CLUSTER_FORMAT = "mongodb+srv://{user}:{password}@{host}/{dbname}"


class Mapper(BaseMapper):

    def __init__(self):
        super().__init__(DbHost, WebDbHost)

    def inner_db_2_web(self, db_object: DbHost, raw: SON):
        pass

    def inner_web_2_db(self, db_object: DbHost, web_object: WebDbHost):

        connection_string_format = ATLAS_CLUSTER_FORMAT
        if web_object.connection_string_format:
            connection_string_format = web_object.connection_string_format

        db_object.alias = web_object.alias
        db_object.name = web_object.name
        db_object.description = web_object.description
        db_object.connection_string_format = connection_string_format
        db_object.db_host = web_object.db_host
        db_object.db_user = web_object.db_user
        db_object.db_password = web_object.db_password
