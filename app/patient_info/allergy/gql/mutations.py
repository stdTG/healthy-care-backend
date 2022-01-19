import graphene

from app.users.common.models.db import PatientUser as DbPatient

from core.logic.base_payload import MutationPayload

from app.patient_info.allergy.models.db import Allergy as Db
from app.patient_info.allergy.models.gql import Allergy as Gql
from app.patient_info.allergy.gql.inputs import AllergyInput, AllergyUpdateInput


class AddAllergy(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = AllergyInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: AllergyInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id).update_one(push__allergies=mh)
        return AddAllergy(uuid=mh.uuid, result=mh)


class UpdateAllergy(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = AllergyUpdateInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: AllergyUpdateInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id, allergies__uuid=record.uuid).update_one(
            set__allergies__S=mh)
        return UpdateAllergy(uuid=mh.uuid, result=mh)


class DeleteAllergy(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        uuid = graphene.UUID(required=True, name="allergyUuid")

    uuid = graphene.UUID()

    async def mutate(self, _, patient_id: str, uuid: str):
        DbPatient.objects(pk=patient_id).update(pull__allergies__uuid=uuid)
        return DeleteAllergy(uuid=uuid)


class AllergyMutations(graphene.Mutation):
    add = AddAllergy.Field()
    delete = DeleteAllergy.Field()
    update = UpdateAllergy.Field()

    async def mutate(self, _):
        return {}
