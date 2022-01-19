import graphene

from core.logic.base_payload import MutationPayload
from .inputs import MedicalConditionInput, MedicalConditionUpdateInput
from ..models.db import MedicalCondition as DbMc, MedicalConditionPatient as DbMcPatient
from ..models.gql import MedicalCondition as GqlMc, MedicalConditionPatient as GqlMcPatient
from app.users.common.models.db import PatientUser as Patient


class AddMedCondition(MutationPayload):
    class Arguments:
        record = MedicalConditionInput(required=True)

    result_uuid = graphene.UUID()
    result = graphene.Field(GqlMcPatient)

    async def mutate(self, _, record: MedicalConditionInput):
        mc: DbMc = DbMc.objects.with_id(record.index)
        mc_patient = DbMcPatient.from_gql(record, mc.name)

        Patient.objects(pk=record.patient_id).update_one(push__medical_conditions=mc_patient)
        return AddMedCondition(result_uuid=mc_patient.uuid, result=GqlMcPatient.from_db(mc_patient))


class UpdateMedCondition(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True)
        record = MedicalConditionUpdateInput(required=True)

    async def mutate(self, _, patient_id: str, record: MedicalConditionUpdateInput):
        Patient.objects(pk=patient_id, medical_conditions__uuid=record.uuid) \
            .update_one(
            set__medical_conditions__S__start=record.start,
            set__medical_conditions__S__end=record.end,
        )
        return UpdateMedCondition()


class DeleteMedCondition(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True)
        uuid = graphene.UUID(required=True)

    async def mutate(self, _, patient_id: str, uuid: str):
        Patient.objects(pk=patient_id).update(pull__medical_conditions__uuid=uuid)
        return DeleteMedCondition()


class MedicalConditionMutations(graphene.Mutation):
    add_to_patient = AddMedCondition.Field()
    delete_from_patient = DeleteMedCondition.Field()
    update_for_patient = UpdateMedCondition.Field()

    async def mutate(self, _):
        return {}
