from __future__ import annotations

from typing import TYPE_CHECKING

from app.patient_info.medical_condition.models.db import MedicalConditionPatient
from app.user_roles import Roles

if TYPE_CHECKING:
    from app.users.dashboard.gql.inputs import PatientUserInput

from mongoengine import Document
from mongoengine.fields import StringField, ObjectIdField, DateField, EmailField, BooleanField
from mongoengine.fields import EmbeddedDocumentField, EmbeddedDocumentListField
from app.models.db import Address

from .sendbird_settings import SendbirdSettings

from app.patient_info.allergy.models.db import Allergy
from app.patient_info.family.models.db import Family
from app.patient_info.lifestyle.models.db import Lifestyle
from app.patient_info.vaccine.models.db import Vaccine


class PatientUser(Document):
    meta = {
        "db_alias": "tenant-db-personal-data",
        "collection": "user_patients",
        "indexes": ["email", "phone", ["$firstName", "$lastName"], ],
        "strict": False
    }

    # core information
    firstName = StringField(required=True)
    lastName = StringField(required=True)
    role = StringField(required=True)
    orgUnitId = ObjectIdField()
    cognito_sub = StringField()
    sendbird: SendbirdSettings = EmbeddedDocumentField(SendbirdSettings)

    # demographics
    language = StringField()
    birthDate = DateField()
    sex = StringField()

    # contacts
    email = EmailField()
    phone = StringField()
    address = EmbeddedDocumentField(Address)

    # other
    photo = StringField()
    photo_content_type = StringField()

    # patient data
    lifestyle = EmbeddedDocumentListField(Lifestyle, default=lambda: list())
    vaccines = EmbeddedDocumentListField(Vaccine, default=lambda: list())
    allergies = EmbeddedDocumentListField(Allergy, default=lambda: list())
    medical_conditions = EmbeddedDocumentListField(MedicalConditionPatient, default=lambda: list())
    family: Family = EmbeddedDocumentField(Family)

    deleted = BooleanField(default=False)

    @classmethod
    def from_gql(cls, gql: PatientUserInput) -> PatientUser:
        db = cls()

        db.firstName = gql.firstName
        db.lastName = gql.lastName

        if gql.byPhone:
            db.phone = gql.byPhone.phone

        if gql.byEmail:
            db.email = gql.byEmail.email

        db.sex = gql.sex

        db.role = str(Roles.PATIENT)

        if gql.birthDate:
            db.birthDate = gql.birthDate

        db.address = Address()
        db.family = Family()

        return db
