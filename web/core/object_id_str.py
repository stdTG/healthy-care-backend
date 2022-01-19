from bson.errors import InvalidId
from bson.objectid import ObjectId


class ObjectIdStr(str):

    def __init__(self, v):
        self = v

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")
        return str(v)
