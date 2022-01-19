from datetime import datetime

from mongoengine import Document
from mongoengine.fields import DateTimeField, DecimalField, ObjectIdField


class Metric(Document):
    meta = {
        "db_alias": "tenant-db-personal-data",
        "collection": "metrics",
        "strict": False
    }

    created = DateTimeField(required=True, default=lambda: datetime.now())
    patient_id = ObjectIdField(required=True)
    value = DecimalField()
    widget_data_type_id = ObjectIdField()
    widget_data_type_name = ObjectIdField()
