import graphene

from .user_dashboard.mutation import DashboardUserMutations
from .user_patient.mutation import PatientUserMutations


class UserMutations(graphene.Mutation):
    dashboard_user = DashboardUserMutations.Field()
    patient_user = PatientUserMutations.Field()

    async def mutate(self, _):
        return {}
