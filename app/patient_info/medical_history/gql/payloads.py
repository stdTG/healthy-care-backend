import graphene

from core.logic.base_payload import PaginationInfo
from ..models.gql import MedicalHistory


class MedHistoryPagination(graphene.ObjectType):
    items = graphene.List(MedicalHistory, required=True)
    page_info = graphene.Field(PaginationInfo, required=True)
