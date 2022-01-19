from mongoengine import Document
from mongoengine.fields import DateTimeField, ObjectIdField, StringField


class Medication(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "medications",
        "strict": False
    }

    name = StringField(required=True)
    created = DateTimeField(required=True)
    patient_id = ObjectIdField(required=True)
