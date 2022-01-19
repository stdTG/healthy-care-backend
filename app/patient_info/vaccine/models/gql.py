import graphene


class Vaccine(graphene.ObjectType):
    uuid = graphene.UUID()
    name = graphene.String(required=True)
    date = graphene.Date()
