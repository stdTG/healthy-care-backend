from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gql.inputs import SubOrgCreateInput, CareTeamCreateInput
from datetime import date

from mongoengine import Document
from mongoengine.fields import (StringField, BooleanField, ObjectIdField, EmbeddedDocumentField,
                                EmbeddedDocumentListField, ListField, DateField, URLField,
                                EmailField)

from app.models.db import Address, WorkingHours
from app.models.db import DayOfWeek


class OrgUnit(Document):
    meta = {
        "db_alias": "tenant-db-basic-data",
        "collection": "org_units",
        "indexes": ["$name", ],
        "strict": False
    }

    parentId = ObjectIdField()
    name = StringField(unique=True, required=True)
    isCareTeam = BooleanField(required=True, default=False)
    isDefaultWorkingHours = BooleanField(default=False)
    description = StringField()

    address = EmbeddedDocumentField(Address)
    site = StringField()
    phone = StringField()
    email = EmailField()
    logo = URLField()
    created = DateField(default=lambda: date.today())
    facebook = StringField()
    linkedin = StringField()
    instagram = StringField()
    language = StringField()

    supervisors = ListField(ObjectIdField())

    workingHours = EmbeddedDocumentListField(WorkingHours, max_length=7)

    @classmethod
    def create_master_org(cls, name: str, default_working_hours: bool = False) -> OrgUnit:
        """Create master organization. It should create only when we create a new workspace."""

        working_hours = []
        if default_working_hours:
            working_hours = [WorkingHours(
                dayOfWeek=DayOfWeek.MONDAY,
                startTime="08:00",
                endTime="20:00",
                startLunchTime="13:00",
                endLunchTime="14:00",
            ), WorkingHours(
                dayOfWeek=DayOfWeek.TUESDAY,
                startTime="08:00",
                endTime="20:00",
                startLunchTime="13:00",
                endLunchTime="14:00",
            ), WorkingHours(
                dayOfWeek=DayOfWeek.WEDNESDAY,
                startTime="08:00",
                endTime="20:00",
                startLunchTime="13:00",
                endLunchTime="14:00",
            ), WorkingHours(
                dayOfWeek=DayOfWeek.THURSDAY,
                startTime="08:00",
                endTime="20:00",
                startLunchTime="13:00",
                endLunchTime="14:00",
            ), WorkingHours(
                dayOfWeek=DayOfWeek.FRIDAY,
                startTime="08:00",
                endTime="20:00",
                startLunchTime="13:00",
                endLunchTime="14:00",
            )]

        return cls(
            name=name,
            parentId=None,
            address=Address(),
            isDefaultWorkingHours=default_working_hours,
            workingHours=working_hours,
        )

    @classmethod
    def from_gql_sub_org(cls, gql: SubOrgCreateInput) -> OrgUnit:
        return cls(
            name=gql.name,
            phone=gql.phone,
            email=gql.email,
            address=Address.from_gql(gql.full_address) if gql.full_address else Address(),
            site=gql.site,
            supervisors=gql.supervisors,
        )

    @classmethod
    def from_gql_care_team(cls, gql: CareTeamCreateInput) -> OrgUnit:
        return cls(
            name=gql.name,
            supervisors=gql.supervisors,
            parentId=gql.sub_org_id,
            isCareTeam=True,
        )
