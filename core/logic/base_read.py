from typing import List, Union

from mongoengine import Document
from pydantic import BaseModel

from core.logic import BaseLogic
from web.core import ObjectIdStr


class BaseRead(BaseLogic):

    async def one_by_id(self, id: ObjectIdStr, map_2_web: bool = False) -> Union[
        Document, BaseModel]:
        db_object: Document = self.db_model_type.objects(id=id).first()
        self.check_exists(db_object, id)

        if map_2_web:
            return self.mapper.db_2_web(db_object)

        return db_object

    async def list_all(self, map_2_web: bool = False) -> Union[List[Document], List[BaseModel]]:
        db_list: List[Document] = self.db_model_type.objects()
        if map_2_web:
            return [self.mapper.db_2_web(db_object) for db_object in db_list]
        return db_list

    async def list_by_ids(self, ids: List[ObjectIdStr], map_2_web: bool = False) -> Union[
        List[Document], List[BaseModel]]:
        db_list: List[Document] = self.db_model_type.objects.filter(refs__in=ids)
        if map_2_web:
            return [self.mapper.db_2_web(db_object) for db_object in db_list]
        return db_list
