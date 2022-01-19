import graphene

from app.care_plans.models.gql import GqlCarePlan


class CarePlanAssignment(graphene.ObjectType):
    care_plan = graphene.Field(GqlCarePlan)
    execution_start_date_time = graphene.DateTime()
    assigment_date_time = graphene.DateTime()
