from mongoengine import Document

from core.logic import BaseLogic
from web.core import ObjectIdStr


class BaseDelete(BaseLogic):

    async def one(self, id: ObjectIdStr) -> dict:
        db_object: Document = self.db_model_type.objects(id=id).first()
        self.check_exists(db_object, id)
        db_object.delete()
        return self.ok_result()
