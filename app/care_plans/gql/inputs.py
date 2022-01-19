import graphene


class CarePlanInput(graphene.InputObjectType):
    id_ = graphene.ID()
    name = graphene.String()
    subtitle = graphene.String()
    description = graphene.String()
    image = graphene.String()
    duration_months = graphene.Int()
    duration_weeks = graphene.Int()
    duration_days = graphene.Int()
    tags = graphene.List(graphene.String)
