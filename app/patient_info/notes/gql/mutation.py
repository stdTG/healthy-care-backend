from datetime import datetime

import graphene

from app.context import get_current_auth
from app.patient_info.notes.gql.inputs import NoteCreateInput, NoteUpdateInput
from app.users.common.models.db import DashboardUser as DbDashboardUser
from core.errors import NotFoundGqlError
from core.logic.base_payload import MutationPayload
from ..models.db import Note as DbNote
from ..models.gql import Note as GqlNote


class CreateNote(MutationPayload):
    class Arguments:
        record = NoteCreateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlNote)

    async def mutate(self, info, record: NoteCreateInput):
        request = info.context['request']
        auth = await get_current_auth(request)
        user = DbDashboardUser.objects(cognito_sub=auth.sub).first()
        db_note = DbNote.from_gql(record, user.id)
        db_note.save()
        return CreateNote(result_id=db_note.id, result=GqlNote.from_db(db_note))


class UpdateNote(MutationPayload):
    class Arguments:
        record = NoteUpdateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlNote)

    async def mutate(self, info, record: NoteUpdateInput):
        db_note: DbNote = DbNote.objects.with_id(record.id_)

        if not db_note:
            return UpdateNote(NotFoundGqlError())

        db_note.title = record.title
        db_note.content = record.content
        db_note.updatedAt = datetime.now()

        db_note.save()

        return UpdateNote(result_id=db_note.id, result=GqlNote.from_db(db_note))


class DeleteNote(MutationPayload):
    class Arguments:
        id_ = graphene.ID(required=True)

    async def mutate(self, info, id_):
        DbNote.objects(pk=id_).delete()
        return DeleteNote()


class NoteMutations(graphene.Mutation):
    create = CreateNote.Field()
    update = UpdateNote.Field()
    delete = DeleteNote.Field()

    async def mutate(self, info):
        return {}
