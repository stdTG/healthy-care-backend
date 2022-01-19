import graphene

from core.errors import NotFoundGqlError
from core.logic.base_payload import MutationPayload
from .inputs import MedicalHistoryInput, MedicalHistoryUpdateInput
from ..models.db import MedicalHistory as DbMedHis
from ..models.gql import MedicalHistory as GqlMedHis


class AddMedHistory(MutationPayload):
    class Arguments:
        record = MedicalHistoryInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlMedHis)

    async def mutate(self, _, record: MedicalHistoryInput):
        mh = DbMedHis.from_gql(record)
        mh.save()
        return AddMedHistory(result_id=mh.id, result=GqlMedHis.from_db(mh))


class UpdateMedHistory(MutationPayload):
    class Arguments:
        id_ = graphene.ID(required=True)
        record = MedicalHistoryUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlMedHis)

    async def mutate(self, _, id_: str, record: MedicalHistoryUpdateInput):
        DbMedHis.objects(pk=id_).update(**record.__dict__)
        med_his = DbMedHis.objects.with_id(id_)
        if not med_his:
            error = NotFoundGqlError(message="Medical history is not found by id")
            return UpdateMedHistory(error=error)
        return UpdateMedHistory(result_id=med_his.id, result=GqlMedHis.from_db(med_his))


class DeleteMedHistory(MutationPayload):
    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, _, id_: str):
        DbMedHis.objects(pk=id_).delete()
        return DeleteMedHistory()


class MedicalHistoryMutations(graphene.Mutation):
    create = AddMedHistory.Field()
    delete = DeleteMedHistory.Field()
    update = UpdateMedHistory.Field()

    def mutate(self, _):
        return {}
