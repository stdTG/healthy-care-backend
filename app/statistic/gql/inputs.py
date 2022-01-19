import graphene


class FilterStatistic(graphene.InputObjectType):
    """use deleted patients for statistic"""
    deleted = graphene.Boolean()
    care_team_id = graphene.ID()
    sub_org_id = graphene.ID()
