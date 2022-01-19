import graphene


class Family(graphene.ObjectType):
    mother = graphene.String()
    father = graphene.String()
    grandparents = graphene.String()
