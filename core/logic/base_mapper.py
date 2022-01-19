from typing import Type

from bson import ObjectId, SON
from mongoengine import Document
from pydantic import BaseModel

from core.utils.strings import dict_w_camel_keys


class BaseMapper:

    def __init__(self, db_model_type: Type[Document] = Document,
                 web_model_type: Type[BaseModel] = BaseModel):
        self.db_model_type = db_model_type
        self.web_model_type = web_model_type

    # DB > WEB

    def str_object_id(self, raw: SON, db_key: str):
        if not raw.has_key(db_key):
            return
        raw[db_key] = str(raw[db_key])

    def inner_db_2_web(self, db_object: Document, raw: SON):
        pass

    def db_2_web(self, db_object: Document) -> BaseModel:
        raw = db_object.to_mongo()
        raw['id'] = str(raw['_id'])

        self.inner_db_2_web(db_object, raw)
        data = dict_w_camel_keys(raw)

        return self.web_model_type.parse_obj(data)

    # WEB > DB

    def object_id(self, db_object: Document, web_object: BaseModel, key: str):
        val = web_object.__getattribute__(key)
        if val is None:
            return
        db_object.__setattr__(key, ObjectId(val))

    def inner_web_2_db(self, db_object: Document, web_object: BaseModel):
        pass

    def web_2_db(self, db_object: Document, web_object: BaseModel):
        self.inner_web_2_db(db_object, web_object)
