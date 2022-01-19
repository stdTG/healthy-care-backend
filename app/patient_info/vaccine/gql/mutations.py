import graphene

from app.users.common.models.db import PatientUser as DbPatient

from core.logic.base_payload import MutationPayload

from app.patient_info.vaccine.models.gql import Vaccine as Gql
from app.patient_info.vaccine.models.db import Vaccine as Db
from app.patient_info.vaccine.gql.inputs import VaccineInput, VaccineUpdateInput


class AddVaccine(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = VaccineInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: VaccineInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id).update_one(push__vaccines=mh)
        return AddVaccine(uuid=mh.uuid, result=mh)


class UpdateVaccine(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = VaccineUpdateInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: VaccineUpdateInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id, vaccines__uuid=record.uuid).update_one(set__vaccines__S=mh)
        return UpdateVaccine(uuid=mh.uuid, result=mh)


class DeleteVaccine(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        uuid = graphene.UUID(required=True, name="vaccineUuid")

    uuid = graphene.UUID()

    async def mutate(self, _, patient_id: str, uuid: str):
        DbPatient.objects(pk=patient_id).update(pull__vaccines__uuid=uuid)
        return DeleteVaccine(uuid=uuid)


class VaccineMutations(graphene.Mutation):
    add = AddVaccine.Field()
    delete = DeleteVaccine.Field()
    update = UpdateVaccine.Field()

    async def mutate(self, _):
        return {}
