import graphene

from core.errors.gql_error import NotAvailableError
from core.logic.base_payload import PaginationInfo
from ..models.gql import Appointment, Event, Timeslot
from ...users.common.models.gql import DashboardUser


class TimeslotPayload(graphene.ObjectType):
    items = graphene.List(Timeslot)


class AppointmentAndEvent(graphene.Union):
    class Meta:
        types = (Event, Appointment,)


class EventAndAppointmentPayload(graphene.ObjectType):
    items = graphene.List(AppointmentAndEvent)


class EventPagination(EventAndAppointmentPayload, ):
    page_info = graphene.Field(PaginationInfo, required=True)


class NotAvailableErrorExtend(NotAvailableError):
    users = graphene.List(DashboardUser)
