from __future__ import annotations

from typing import TYPE_CHECKING

from app.context import get_fields, get_loader

if TYPE_CHECKING:
    from .db import Appointment as DbAppointment

import graphene

from app.org_units.model_gql import SubOrganization
from app.users.common.models.gql import DashboardUser as User
from app.users.common.models.gql import PatientUser as Patient
from .db import AppointmentStatus as DbAppointmentStatus
from .db import EventType as DbEventType


class EventType(graphene.Enum):
    CONSULTATION = DbEventType.CONSULTATION
    VACCINATION = DbEventType.VACCINATION
    OTHER = DbEventType.OTHER


class AppointmentStatus(graphene.Enum):
    AWAITING = DbAppointmentStatus.AWAITING
    APPROVED = DbAppointmentStatus.APPROVED
    REJECTED = DbAppointmentStatus.REJECTED
    CANCELLED = DbAppointmentStatus.CANCELLED


class Timeslot(graphene.ObjectType):
    start_time = graphene.DateTime()
    end_time = graphene.DateTime()


class UserWithStatus(User):
    status = AppointmentStatus(required=True)


class PatientWithStatus(Patient):
    status = AppointmentStatus(required=True)


class EventBase(graphene.ObjectType):
    id_ = graphene.ID()
    title = graphene.String()
    event_type = EventType()
    is_appointment = graphene.Boolean()
    location = graphene.Field(lambda: SubOrganization)
    is_online = graphene.Boolean()

    start_date = graphene.DateTime()
    end_date = graphene.DateTime()

    created_at = graphene.Date()
    created_by = graphene.Field(lambda: User)

    @staticmethod
    async def resolve_created_by(root, info):
        fields = get_fields(info)
        if root.created_by and not (len(fields) == 1 and "id_" in fields):
            loader = await get_loader(info, "user_by_id")
            db_user = await loader.load(root.created_by)
            return User.from_db(db_user)

        else:
            return User(id_=root.created_by)

    @staticmethod
    async def resolve_location(root, info):
        if root.location:
            loader = await get_loader(info, "org_unit_by_id")
            res = await loader.load(root.location)

            if res.isCareTeam:
                return None

            return SubOrganization.from_db(res)
        else:
            return None


class Appointment(EventBase):
    note = graphene.String()
    patient = graphene.Field(lambda: PatientWithStatus)
    user = graphene.Field(lambda: UserWithStatus)

    @classmethod
    def from_db(cls, db: DbAppointment) -> Appointment:
        patient, = db.patients
        user, = db.users
        return cls(
            id_=db.id,
            title=db.title,
            event_type=db.eventType,
            note=db.note,
            start_date=db.startDate,
            end_date=db.endDate,
            patient=patient,
            user=user,
            location=db.location,
            is_online=not bool(db.location),
            is_appointment=db.isAppointment,
            created_by=db.createdById,
            created_at=db.createdAt,
        )

    @staticmethod
    async def resolve_patient(root, info):
        resolved_patient = None
        fields = get_fields(info)

        if not ((len(fields) == 1 and ("id_" in fields or "status" in fields)) or
                (len(fields) == 2 and {"id_", "status"} == fields)):

            loader = await get_loader(info, "patient_by_id")
            user = await loader.load(root.patient.id)

            resolved_patient = PatientWithStatus.from_db(user)
            resolved_patient.status = root.patient.status

        else:
            resolved_patient = PatientWithStatus()
            resolved_patient.id_ = root.patient.id
            resolved_patient.status = root.patient.status

        return resolved_patient

    @staticmethod
    async def resolve_user(root, info):
        resolved_user = None
        fields = get_fields(info)

        if not ((len(fields) == 1 and ("id_" in fields or "status" in fields)) or
                (len(fields) == 2 and {"id_", "status"} == fields)):

            loader = await get_loader(info, "user_by_id")
            user = await loader.load(root.user.id)

            resolved_user = UserWithStatus.from_db(user)
            resolved_user.status = root.user.status

        else:
            resolved_user = UserWithStatus()
            resolved_user.id_ = root.user.id
            resolved_user.status = root.user.status

        return resolved_user


class Event(EventBase):

    patients = graphene.List(lambda: PatientWithStatus)
    users = graphene.List(lambda: UserWithStatus)

    @classmethod
    def from_db(cls, db: DbAppointment) -> Event:
        return cls(
            id_=db.id,
            title=db.title,
            start_date=db.startDate,
            end_date=db.endDate,
            location=db.location,
            is_online=not bool(db.location),
            created_by=db.createdById,
            patients=db.patients,
            users=db.users,
            is_appointment=db.isAppointment,
            created_at=db.createdAt,
        )

    @staticmethod
    async def resolve_patients(root, info):
        resolved_patients = []
        fields = get_fields(info)

        if not ((len(fields) == 1 and ("id_" in fields or "status" in fields)) or
                (len(fields) == 2 and ["id_", "status"] in fields)):

            loader = await get_loader(info, "patient_by_id")
            patients = await loader.load_many([patient.id for patient in root.patients])

            for patient, root_patient in zip(patients, root.patients):
                resolved_patient = PatientWithStatus.from_db(patient)
                resolved_patient.status = root_patient.status

                resolved_patients.append(resolved_patient)

        else:
            for patient in root.patients:
                resolved_patient = PatientWithStatus()
                resolved_patient.id_ = patient.id
                resolved_patient.status = patient.status

                resolved_patients.append(resolved_patient)

        return resolved_patients

    @staticmethod
    async def resolve_users(root, info):
        resolved_users = []
        fields = get_fields(info)

        if not ((len(fields) == 1 and ("id_" in fields or "status" in fields)) or
                (len(fields) == 2 and ["id_", "status"] in fields)):

            loader = await get_loader(info, "user_by_id")
            users = await loader.load_many([user.id for user in root.users])

            for user, root_user in zip(users, root.users):
                resolved_user = UserWithStatus.from_db(user)
                resolved_user.status = root_user.status

                resolved_users.append(resolved_user)

        else:
            for user in root.users:
                resolved_user = UserWithStatus()
                resolved_user.id_ = user.id
                resolved_user.status = user.status

                resolved_users.append(resolved_user)

        return resolved_users
