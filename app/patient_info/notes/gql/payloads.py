import graphene

from core.logic.base_payload import PaginationInfo
from ..models.gql import Note as GqlNote


class NotePagination(graphene.ObjectType):
    items = graphene.List(GqlNote, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)
