import graphene


class Allergy(graphene.ObjectType):
    uuid = graphene.UUID()
    name = graphene.String(required=True)
    date = graphene.Date()
