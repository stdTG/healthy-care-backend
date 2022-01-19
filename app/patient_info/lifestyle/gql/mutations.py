import graphene

from app.users.common.models.db import PatientUser as DbPatient

from core.logic.base_payload import MutationPayload

from app.patient_info.lifestyle.models.gql import Lifestyle as Gql
from app.patient_info.lifestyle.models.db import Lifestyle as Db
from app.patient_info.lifestyle.gql.inputs import LifestyleInput, LifestyleUpdateInput


class AddLifestyle(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = LifestyleInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: LifestyleInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id).update_one(push__lifestyle=mh)
        return AddLifestyle(uuid=mh.uuid, result=mh)


class UpdateLifestyle(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        record = LifestyleUpdateInput(required=True)

    uuid = graphene.UUID()
    result = graphene.Field(Gql)

    async def mutate(self, _, patient_id: str, record: LifestyleUpdateInput):
        mh = Db(**record.__dict__)
        DbPatient.objects(pk=patient_id, lifestyle__uuid=record.uuid).update_one(
            set__lifestyle__S=mh)
        return UpdateLifestyle(uuid=mh.uuid, result=mh)


class DeleteLifestyle(MutationPayload):
    class Arguments:
        patient_id = graphene.ID(required=True, name="patient")
        uuid = graphene.UUID(required=True, name="lifestyleUuid")

    uuid = graphene.UUID()

    async def mutate(self, _, patient_id: str, uuid: str):
        DbPatient.objects(pk=patient_id).update(pull__lifestyle__uuid=uuid)
        return DeleteLifestyle(uuid=uuid)


class LifestyleMutations(graphene.Mutation):
    add = AddLifestyle.Field()
    delete = DeleteLifestyle.Field()
    update = UpdateLifestyle.Field()

    async def mutate(self, _):
        return {}
