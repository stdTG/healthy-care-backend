from __future__ import annotations

from typing import TYPE_CHECKING

from app.context import get_loader

if TYPE_CHECKING:
    from ..db.user_dashboard import DashboardUser as DbDashboardUser
    from app.org_units.model_db import OrgUnit

import graphene

from app.models.gql import Address
from app.models.gql import WorkingHours
from .role import RoleEnum
from .sex import SexEnum
from .user import User, UserByPhone, UserByEmail


class SpecialityEnum(graphene.Enum):
    DOCTOR = "doctor"


class DashboardUser(User, graphene.ObjectType):
    role = RoleEnum()
    org_unit = graphene.Field("app.org_units.model_gql.OrgUnitPayload")
    speciality = SpecialityEnum()
    description = graphene.String()
    title = graphene.String()
    memberSince = graphene.Date()
    fullAddress = graphene.Field(Address)
    sex = SexEnum(default_value=SexEnum.UNDEFINED)
    birthDate = graphene.Date()
    status = graphene.String()

    duration = graphene.Int()
    working_hours = graphene.List(WorkingHours)

    @property
    def org_unit_class(self):
        return self._meta.fields['org_unit'].type

    @classmethod
    def from_db(cls, db_user: DbDashboardUser) -> DashboardUser:
        gql_user = cls(
            id_=db_user.id,
            firstName=db_user.firstName,
            lastName=db_user.lastName,
            role=db_user.role,
            birthDate=db_user.birthDate,
            language=db_user.language,
            org_unit=db_user.orgUnitId,
            speciality=db_user.speciality,
            description=db_user.description,
            title=db_user.title,
            memberSince=db_user.memberSince,
            sex=db_user.sex,
            status=db_user.status,
            duration=db_user.duration,
        )

        if db_user.phone:
            by_phone = UserByPhone()
            by_phone.phone = db_user.phone
            gql_user.byPhone = by_phone

        if db_user.email:
            by_email = UserByEmail()
            by_email.email = db_user.email
            gql_user.byEmail = by_email

        if db_user.address:
            gql_user.fullAddress = Address.from_db(db_user.address)

        gql_user.working_hours = [WorkingHours.from_db(working_hours) for working_hours in
                                  db_user.workingHours]

        return gql_user

    @staticmethod
    async def resolve_org_unit(root, info):
        if root.org_unit:
            loader = await get_loader(info, "org_unit_by_id")
            res: OrgUnit = await loader.load(root.org_unit)
            assert root.org_unit == res.id
            if res.isCareTeam:
                return root.org_unit_class.care_team_from_db(res)
            else:
                return root.org_unit_class.sub_org_from_db(res)
