from mongoengine import Document
from mongoengine.fields import DateTimeField, EmailField, IntField, ObjectIdField, StringField


class UserVerification(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "user_verifications",
        "indexes": ["username", "token"],
        "strict": False
    }

    user_id = ObjectIdField()
    type_ = StringField(db_field="type")
    username = StringField()
    token = StringField()
    tokenExpires = DateTimeField()
    code = StringField()
    attempts = IntField()
    status = StringField()
