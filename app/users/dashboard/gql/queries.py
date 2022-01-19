import graphene

from .user_dashboard.query import DashboardUserQueries
from .user_patient.query import PatientUserQueries


class UserQueries(graphene.ObjectType):
    dashboard = graphene.Field(DashboardUserQueries)
    patient = graphene.Field(PatientUserQueries)

    async def resolve_dashboard(self, _):
        return {}

    async def resolve_patient(self, _):
        return {}
