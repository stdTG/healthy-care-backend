import graphene


class AllergyInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    date = graphene.Date()


class AllergyUpdateInput(AllergyInput):
    uuid = graphene.UUID(required=True)
