from typing import List, Optional, Union

from mongoengine import Document
from pydantic import BaseModel

from core.logic import BaseLogic


class BaseCreate(BaseLogic):

    async def one(self, web_object: BaseModel, map_2_web: bool = False) -> Union[
        Optional[Document], Optional[dict]]:
        db_object: Document = self.db_model_type()
        self.mapper.web_2_db(db_object, web_object)
        db_object.save()
        if map_2_web:
            return self.new_object_result(db_object)
        return db_object

    async def many(self, web_list: List[BaseModel]) -> List[Document]:
        result = []
        for web_object in web_list:
            db_object: Document = self.db_model_type()
            self.mapper.web_2_db(db_object, web_object)
            result.append(db_object)

        await self.db_model_type.objects.insert()
        return result
