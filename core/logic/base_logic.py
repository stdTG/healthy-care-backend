from typing import Optional, Type

from mongoengine import Document
from pydantic import BaseModel

from core.errors import *
from web.core import ObjectIdStr
from .base_mapper import BaseMapper


class BaseLogic:
    logic_name: str = "Base"
    mapper: BaseMapper

    def __init__(
            self,
            db_model_type: Type[Document] = Document,
            web_model_type: Type[BaseModel] = BaseModel,
            mapper: BaseMapper = BaseMapper()
    ):
        self.db_model_type = db_model_type
        self.web_model_type = web_model_type
        self.mapper = mapper

    def not_found_error(self, object_id):
        return "[{logic_name}] Object not found. ID = {id}".format(
            logic_name=self.logic_name, id=object_id
        )

    def check_exists(self, db_object: Optional[Document], id: ObjectIdStr):
        if db_object:
            return
        raise HTTPNotFoundError(self.not_found_error(id))

    def new_object_result(self, db_object: Document):
        return db_object

    def ok_result(self):
        return self.db_model_type
