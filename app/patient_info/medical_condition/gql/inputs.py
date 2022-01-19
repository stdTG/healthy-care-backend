import graphene

from core.gql.types import GrapheneMongoId


class MedicalConditionInput(graphene.InputObjectType):
    index = graphene.ID(required=True)
    start = graphene.Date(required=True, name="startDate")
    end = graphene.Date(name="endDate")
    patient_id = GrapheneMongoId(required=True)


class MedicalConditionUpdateInput(graphene.InputObjectType):
    uuid = graphene.UUID(required=True)
    start = graphene.Date(required=True, name="startDate")
    end = graphene.Date(name="endDate")
