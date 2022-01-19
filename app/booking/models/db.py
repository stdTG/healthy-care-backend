from __future__ import annotations

from typing import List, TYPE_CHECKING

from bson import ObjectId

if TYPE_CHECKING:
    from ..gql.inputs import AppointmentCreateInput, EventCreateInput

from datetime import date

from mongoengine import ObjectIdField, Document, EmbeddedDocument, EmbeddedDocumentListField
from mongoengine.fields import StringField, DateField, DateTimeField, BooleanField

from core.utils.str_enum import StrEnum


class AppointmentStatus(StrEnum):
    AWAITING = "awaiting"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EventType(StrEnum):
    CONSULTATION = "consultation"
    VACCINATION = "vaccination"
    OTHER = "other"


class StatusInfo(EmbeddedDocument):
    id = ObjectIdField(required=True)
    status = StringField(required=True, choices=AppointmentStatus)


class Appointment(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "appointments",
        "strict": False
    }

    title = StringField()
    eventType = StringField(choices=EventType)
    note = StringField()

    startDate = DateTimeField()
    endDate = DateTimeField()

    location = ObjectIdField()  # if None then appointment will be offline

    createdAt = DateField(required=True, default=lambda: date.today())
    createdById = ObjectIdField(required=True)
    isAppointment = BooleanField(default=True)

    patients = EmbeddedDocumentListField(StatusInfo)
    users = EmbeddedDocumentListField(StatusInfo)

    @classmethod
    def from_gql_appointment(cls, gql: AppointmentCreateInput, created_by_id: ObjectId,
                             location_id: ObjectId) -> Appointment:
        return cls(
            title=gql.title,
            eventType=gql.event_type,
            note=gql.note,
            startDate=gql.start_date,
            endDate=gql.end_date,
            location=location_id,
            patients=[StatusInfo(id=gql.patient, status=AppointmentStatus.AWAITING), ],
            users=[StatusInfo(id=gql.user if gql.user else created_by_id,
                              status=AppointmentStatus.APPROVED), ],
            createdById=created_by_id,
        )

    @classmethod
    def from_gql_event(cls, gql: EventCreateInput, created_by_id: ObjectId,
                       location_id: ObjectId) -> Appointment:
        return cls(
            title=gql.title,
            startDate=gql.start_date,
            endDate=gql.end_date,
            patients=cls.create_statuses(gql.patients, AppointmentStatus.AWAITING),
            users=cls.create_statuses(gql.users, AppointmentStatus.APPROVED),
            location=location_id,
            createdById=created_by_id,
            isAppointment=False,
        )

    @classmethod
    def create_statuses(cls, ids: List[str], status: AppointmentStatus) -> List[StatusInfo]:
        statuses = []
        if not ids:
            return statuses

        for id_ in ids:
            statuses.append(
                StatusInfo(
                    id=id_,
                    status=status,
                )
            )

        return statuses
