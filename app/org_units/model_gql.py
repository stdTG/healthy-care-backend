from __future__ import annotations

from typing import Dict, TYPE_CHECKING, Union

if TYPE_CHECKING:
    ...

import graphene

from app.models.gql import WorkingHours as GqlWorkingHours
from app.models.gql import Address as GqlAddress
from app.users.common.models.db.user_dashboard import DashboardUser as DbUser
from .model_db import OrgUnit as DbOrgUnit
from app.users.common.models.gql import DashboardUser as User
from app.context import get_fields, get_loader


class UserByCareTeamMixin:
    @staticmethod
    async def resolve_users(root, info):
        loader = await get_loader(info, "user_by_org_unit")
        res = await loader.load(root.id_)

        # TODO delete after test on big data
        for i in res or []:
            assert i.orgUnitId == root.id_

        return [User.from_db(db_user) for db_user in res or []]


class SupervisorMixin:
    @staticmethod
    async def resolve_supervisors(root, info):
        fields = get_fields(info)
        if root.supervisors and not (len(fields) == 1 and "id_" in fields):
            loader = await get_loader(info, "user_by_id")
            res = await loader.load_many(root.supervisors)
            return [User.from_db(db_user) for db_user in res]

        else:
            return [User(id_=id_) for id_ in root.supervisors]


class Organization:
    name = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    full_address = graphene.Field(GqlAddress)
    site = graphene.String()
    working_hours = graphene.List(GqlWorkingHours)


class SubOrganization(Organization, SupervisorMixin, graphene.ObjectType):
    id_ = graphene.ID()
    supervisors = graphene.List(lambda: User)
    users = graphene.List(lambda: User)
    care_teams = graphene.List(lambda: CareTeam)
    care_teams_count = graphene.Int()
    users_count = graphene.Int()

    @classmethod
    def from_db(cls, db: DbOrgUnit) -> SubOrganization:
        gql_address = GqlAddress()
        working_hours = []
        if db.address:
            gql_address = GqlAddress.from_db(db.address)
        if db.workingHours:
            working_hours = [GqlWorkingHours.from_db(working_hours) for working_hours in
                             db.workingHours]

        return cls(
            id_=db.id,
            name=db.name,
            phone=db.phone,
            email=db.email,
            full_address=gql_address,
            site=db.site,
            working_hours=working_hours,
            supervisors=db.supervisors,
        )

    @staticmethod
    async def resolve_care_teams_count(root, info):
        # TODO should be use dataloader
        return DbOrgUnit.objects(parentId=root.id_).count()

    @staticmethod
    async def resolve_care_teams(root, info):
        loader = await get_loader(info, "care_team_by_sub_org")
        res = await loader.load(root.id_)

        if not res:
            return []

        assert res.get("_id") == root.id_
        care_teams = res.get("careTeams")

        gql = []
        for care_team in care_teams:
            gql.append(CareTeam.from_db(care_team))

        return gql

    @staticmethod
    async def resolve_users_count(root, info):
        # TODO should be use dataloader
        care_teams = DbOrgUnit.objects(parentId=root.id_).all()
        ids = [cm.id for cm in care_teams]
        ids.append(root.id_)
        return DbUser.objects(orgUnitId__in=ids, deleted__ne=True).count()

    @staticmethod
    async def resolve_users(root, info):
        loader = await get_loader(info, "user_by_org_unit")
        care_teams = DbOrgUnit.objects(parentId=root.id_).all()
        ids = [cm.id for cm in care_teams]
        ids.append(root.id_)

        res_list = await loader.load_many(ids)

        users = []
        for res in res_list:
            for user in res or []:
                # TODO delete after test on big data
                assert user.orgUnitId in ids
                users.append(User.from_db(user))

        return users


class CareTeam(UserByCareTeamMixin, SupervisorMixin, graphene.ObjectType, ):
    id_ = graphene.ID()
    sub_org = graphene.Field(lambda: SubOrganization)
    name = graphene.String()
    supervisors = graphene.List(lambda: User)
    users = graphene.List(lambda: User)

    @classmethod
    def from_db(cls, db: Union[DbOrgUnit, Dict]) -> CareTeam:
        if isinstance(db, DbOrgUnit):
            return cls(
                id_=db.id,
                name=db.name,
                sub_org=db.parentId,
                supervisors=db.supervisors,
            )
        else:
            return cls(
                id_=db.get("_id"),
                name=db.get("name"),
                sub_org=db.get("parentId"),
                supervisors=db.get("supervisors"),
            )

    @staticmethod
    async def resolve_sub_org(root, info):
        if root.sub_org:
            loader = await get_loader(info, "org_unit_by_id")
            res = await loader.load(root.sub_org)

            if res.isCareTeam:
                return None

            return SubOrganization.from_db(res)
        else:
            return None


class MasterOrganization(Organization, graphene.ObjectType):
    is_default_working_hours = graphene.Boolean()
    logo = graphene.String()
    created = graphene.Date()
    language = graphene.String()
    facebook = graphene.String()
    instagram = graphene.String()
    linkedin = graphene.String()
    description = graphene.String()

    @classmethod
    def from_db(cls, db: DbOrgUnit) -> MasterOrganization:
        gql_address = GqlAddress()
        working_hours = []
        if db.address:
            gql_address = GqlAddress.from_db(db.address)
        if db.workingHours:
            working_hours = [GqlWorkingHours.from_db(working_hours) for working_hours in
                             db.workingHours]

        return cls(
            name=db.name,
            phone=db.phone,
            email=db.email,
            full_address=gql_address,
            site=db.site,
            is_default_working_hours=db.isDefaultWorkingHours,
            working_hours=working_hours,
            logo=db.logo,
            created=db.created,
            language=db.language,
            facebook=db.facebook,
            linkedin=db.linkedin,
            description=db.description,
            instagram=db.instagram,
        )


class OrgUnitPayload(graphene.Union):
    care_team_from_db = CareTeam.from_db
    sub_org_from_db = SubOrganization.from_db

    class Meta:
        types = (SubOrganization, CareTeam)
