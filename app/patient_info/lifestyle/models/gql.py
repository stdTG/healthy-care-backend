import graphene


class Lifestyle(graphene.ObjectType):
    uuid = graphene.UUID()
    activity = graphene.String(required=True)
    description = graphene.String()
