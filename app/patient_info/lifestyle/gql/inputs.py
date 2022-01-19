import graphene


class LifestyleInput(graphene.InputObjectType):
    activity = graphene.String(required=True)
    description = graphene.String(required=True)


class LifestyleUpdateInput(LifestyleInput):
    uuid = graphene.UUID(required=True)