import graphene


class Item(graphene.ObjectType):
    key = graphene.String()
    value = graphene.Int()


class StatisticPayload(graphene.ObjectType):
    items = graphene.List(Item)
