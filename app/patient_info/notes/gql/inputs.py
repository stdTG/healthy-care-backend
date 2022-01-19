import graphene


class NoteCreateInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String()
    patient = graphene.ID(required=True)


class NoteUpdateInput(graphene.InputObjectType):
    id_ = graphene.ID(required=True)
    title = graphene.String(required=True)
    content = graphene.String()
