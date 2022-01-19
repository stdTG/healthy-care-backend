import graphene


class FamilyInput(graphene.InputObjectType):
    mother = graphene.String()
    father = graphene.String()
    grandparents = graphene.String()
