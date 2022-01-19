import graphene
from aiodataloader import DataLoader
from fastapi import APIRouter, Depends, Request
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.graphql import GraphQLApp

from app.booking.gql.mutation import ScheduleMutations
from app.booking.gql.query import ScheduleQueries
from app.care_plans.gql.mutation import CarePlanMutations
from app.care_plans.gql.query import CarePlanQueries
from app.org_units.gql.mutation import OrgUnitMutations
from app.org_units.gql.query import OrgUnitQueries
from app.org_units.logic.utils import get_care_teams, get_orgs
from app.patient_info.gql import PatientInfoMutations, PatientInfoQueries
from app.statistic.gql.query import StatisticsQueries
from app.user_roles import Roles
from app.users.dashboard.gql.mutation import UserMutations
from app.users.dashboard.gql.queries import UserQueries
from app.users.dashboard.logic.utils import get_patients, get_users, get_users_by_org_unit
from core.errors import *
from core.factory.cloudauth import get_current_auth
from core.factory.web import get_current_app
from web.cloudauth.auth_claims import AuthClaims
from web.cloudauth.auth_current_user import AuthCurrentUser

router = APIRouter()
get_current_user = AuthCurrentUser()


class Queries(graphene.ObjectType):
    user = graphene.Field(UserQueries)
    care_plan = graphene.Field(CarePlanQueries)
    statistics = graphene.Field(StatisticsQueries)
    schedule = graphene.Field(ScheduleQueries)
    org_unit = graphene.Field(OrgUnitQueries)
    patient_info = graphene.Field(PatientInfoQueries)

    async def resolve_user(self, _):
        return {}

    async def resolve_care_plan(self, _):
        return {}

    async def resolve_statistics(self, _):
        return {}

    async def resolve_schedule(self, _):
        return {}

    async def resolve_org_unit(self, _):
        return {}

    async def resolve_patient_info(self, _):
        return {}


class Mutations(graphene.Mutation):
    user = UserMutations.Field()
    care_plan = CarePlanMutations.Field()
    org_unit = OrgUnitMutations.Field()
    schedule = ScheduleMutations.Field()
    patient_info = PatientInfoMutations.Field()

    async def mutate(self, _):
        return {}


def create_loaders():
    return {
        "user_by_id": DataLoader(get_users),
        "user_by_org_unit": DataLoader(get_users_by_org_unit),
        "patient_by_id": DataLoader(get_patients),
        "org_unit_by_id": DataLoader(get_orgs),
        "care_team_by_sub_org": DataLoader(get_care_teams),
    }


@router.get("/graphql")
@router.post("/graphql")
async def graphql(request: Request, current_user: AuthClaims = Depends(get_current_user)):
    types = [
        GqlError, TitleAlreadyTakenGqlError, ServerGqlError, ValidationGqlError, NotFoundGqlError,
        NotAvailableGqlError,
    ]
    schema = graphene.Schema(query=Queries, mutation=Mutations, types=types)
    graphql_app = GraphQLApp(schema=schema, executor_class=AsyncioExecutor)

    request.state.auth_claims = current_user
    request.state.loaders = create_loaders()
    return await graphql_app.handle_graphql(request=request)


def init_graphql():
    auth = get_current_auth()
    app = get_current_app()

    app.include_router(router, dependencies=[
        Depends(auth.allow(Roles.ALL_EXCEPT_PATIENT, ""))
    ])

    app.add_route("/testgraphql", GraphQLApp(schema=graphene.Schema(query=Queries, mutation=Mutations), executor_class=AsyncioExecutor))

