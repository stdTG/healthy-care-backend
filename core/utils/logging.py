import datetime
import traceback

from mongoengine import Document
from mongoengine.fields import DateTimeField, StringField


class LogRecordDb(Document):
    meta = {
        "db_alias": "master-db",
        "collection": "logs",
        "strict": False
    }

    type_ = StringField(required=True, db_field="type")
    created = DateTimeField(required=True)
    details = StringField()
    stacktrace = StringField()


class Logger:

    def __init__(self):
        pass

    def put_record(self, type_, details, tb):
        record = LogRecordDb()
        record.type_ = type_
        record.created = datetime.datetime.utcnow()
        record.details = details
        record.stacktrace = tb
        record.save()

    def error(self, err):
        tb = traceback.format_exc()
        print("[ERROR] \n", err, "\n", tb)
        self.put_record("error", str(err), tb)
