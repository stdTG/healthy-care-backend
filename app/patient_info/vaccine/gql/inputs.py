import graphene


class VaccineInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    date = graphene.Date()


class VaccineUpdateInput(VaccineInput):
    uuid = graphene.UUID(required=True)

