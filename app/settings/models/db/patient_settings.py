from mongoengine import Document
from mongoengine.fields import ListField, ObjectIdField, StringField

from app.measurement_units.models.db import UnitDistance, UnitTemperature, UnitWeight
from .language import Language


class PatientSettings(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "user_patient_settings",
        "indexes": ["patientId", "cognitoSub"],
        "strict": False
    }

    patientId = ObjectIdField(required=True)
    cognitoSub = StringField(required=True)

    weightUnit = StringField(default=UnitWeight.kg)
    distanceUnit = StringField(default=UnitDistance.metric)
    temperatureUnit = StringField(default=UnitTemperature.celsius)

    remindersNotification = ListField()
    appointmentsNotification = ListField()
    messagesNotification = ListField()

    language = StringField(default=Language.english)
