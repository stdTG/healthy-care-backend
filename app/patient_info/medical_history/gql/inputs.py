import graphene


class MedicalHistoryInput(graphene.InputObjectType):
    patient_id = graphene.ID(required=True, name="patient")
    name = graphene.String(required=True)
    comment = graphene.String()
    date = graphene.Date()


class MedicalHistoryUpdateInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    comment = graphene.String()
    date = graphene.Date()
