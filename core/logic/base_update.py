from mongoengine import Document
from pydantic import BaseModel

from core.logic import BaseLogic


class BaseUpdate(BaseLogic):

    async def one(self, web_object: BaseModel) -> Document:
        db_object: Document = self.db_model_type.objects(id=web_object.id).first()

        self.check_exists(db_object, web_object.id)
        self.mapper.web_2_db(db_object, web_object)

        db_object.save()
        return self.ok_result()
