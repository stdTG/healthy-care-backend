import graphene

from core.logic.base_payload import MutationPayload
from core.errors import NotFoundGqlError, TitleAlreadyTakenGqlError, ValidationGqlError

from app.users.common.models.gql import PatientUser as GqlPatientUser
from app.users.common.models.db import PatientUser as DbPatientUser


from app.patient_info.family.models.gql import Family as Gql
from app.patient_info.family.models.db import Family as Db
from app.patient_info.family.gql.inputs import FamilyInput


class UpdateFamily(MutationPayload):
    """Mutation to update patient`s family information."""

    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = FamilyInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlPatientUser)

    async def mutate(self, _, patient_id: str, record: FamilyInput):
        from app.users.dashboard.gql.user_patient.mutation import UpdatePatient

        patient: DbPatientUser = DbPatientUser.objects.with_id(patient_id)
        if not patient:
            error = NotFoundGqlError(message="Patient-user is not found by id")
            return UpdatePatient(error=error)

        if record.grandparents is not None:
            patient.family.grandparents = [record.grandparents]

        if record.mother is not None:
            patient.family.mother = [record.mother]

        if record.father is not None:
            patient.family.father = [record.father]

        patient.save()

        return UpdatePatient(result_id=patient.id, result=GqlPatientUser.from_db(patient))
