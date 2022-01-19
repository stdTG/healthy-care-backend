import graphene

from .medical_condition.gql.mutations import MedicalConditionMutations
from .medical_condition.gql.query import MedicalConditionQueries
from .medical_history.gql.mutations import MedicalHistoryMutations
from .medical_history.gql.query import MedicalHistoryQueries
from .metrics.gql.query import MetricQueries
from .notes.gql.mutation import NoteMutations
from .notes.gql.query import NoteQueries


class PatientInfoMutations(graphene.Mutation):
    note = NoteMutations.Field()
    medical_history = MedicalHistoryMutations.Field()
    medical_condition = MedicalConditionMutations.Field()

    async def mutate(self, _):
        return {}


class PatientInfoQueries(graphene.ObjectType):
    note = graphene.Field(NoteQueries)
    medical_history = graphene.Field(MedicalHistoryQueries)
    medical_condition = graphene.Field(MedicalConditionQueries)
    metric = graphene.Field(MetricQueries)

    async def resolve_note(self, _):
        return {}

    async def resolve_metric(self, _):
        return {}

    async def resolve_medical_history(self, _):
        return {}

    async def resolve_medical_condition(self, _):
        return {}
