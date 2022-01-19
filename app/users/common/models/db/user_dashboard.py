from __future__ import annotations

from collections import namedtuple
from typing import TYPE_CHECKING

from app.users.common.models.db import SendbirdSettings

if TYPE_CHECKING:
    from app.users.dashboard.gql.inputs import DashboardUserInput

from datetime import date

from mongoengine import Document
from mongoengine.fields import (BooleanField, StringField, ObjectIdField, DateField, EmailField,
                                IntField)
from mongoengine.fields import EmbeddedDocumentField, EmbeddedDocumentListField

from app.models.db import Address, WorkingHours

CognitoUser = namedtuple("CognitoUser",
                         ["email", "phone", "password", "role", "orgUnitId", "send_email",
                          "send_sms"]
                         )


class DashboardUser(Document):
    meta = {
        "db_alias": "tenant-db-personal-data",
        "collection": "users_dashboard",
        "strict": False
    }

    # core information
    firstName = StringField(required=True)
    lastName = StringField(required=True)
    role = StringField(required=True)
    orgUnitId = ObjectIdField()
    memberSince = DateField(required=True, default=lambda: date.today())
    cognito_sub = StringField()
    sendbird = EmbeddedDocumentField(SendbirdSettings)

    # demographics
    language = StringField()
    birthDate = DateField()
    sex = StringField()

    # contacts
    email = EmailField(required=True)
    phone = StringField()
    address = EmbeddedDocumentField(Address)

    # other
    photo = StringField()

    speciality = StringField()
    description = StringField()
    title = StringField()
    status = StringField()
    workingHours = EmbeddedDocumentListField(WorkingHours)
    duration = IntField(default=30)

    deleted = BooleanField(default=False)

    @classmethod
    def from_gql(cls, gql: DashboardUserInput) -> DashboardUser:
        db_user = cls()

        if hasattr(gql, "firstName"):
            db_user.firstName = gql.firstName
        else:
            db_user.firstName = ""

        if hasattr(gql, "lastName"):
            db_user.lastName = gql.lastName
        else:
            db_user.lastName = ""

        db_user.phone = gql.phone
        db_user.email = gql.email

        db_user.role = gql.role

        if gql.orgUnitId:
            db_user.orgUnitId = gql.orgUnitId

        return db_user
