import graphene

from core.gql.types import GrapheneMongoId
from ..models.gql import EventType


class AppointmentCreateInput(graphene.InputObjectType):
    title = graphene.String()
    event_type = EventType(required=True)
    start_date = graphene.DateTime(required=True)
    end_date = graphene.DateTime(required=True)

    patient = GrapheneMongoId(required=True)
    user = GrapheneMongoId()
    is_online = graphene.Boolean(required=True)

    note = graphene.String()


class EventCreateInput(graphene.InputObjectType):
    title = graphene.String()

    patients = graphene.List(GrapheneMongoId)
    users = graphene.List(GrapheneMongoId)

    is_online = graphene.Boolean(required=True)

    start_date = graphene.DateTime(required=True)
    end_date = graphene.DateTime(required=True)


class FilterFindManyAppointment(graphene.InputObjectType):
    start_date = graphene.Date()
    end_date = graphene.Date()
    user = GrapheneMongoId()
    patient = GrapheneMongoId()


class FilterFindManyTimeSlot(graphene.InputObjectType):
    date = graphene.Date(required=True)
    user = GrapheneMongoId()


class RescheduleAppointmentInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    start_date = graphene.DateTime(required=True)
    end_date = graphene.DateTime(required=True)


class RescheduleEventInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    start_date = graphene.DateTime(required=True)
    end_date = graphene.DateTime(required=True)


class UpdateAppointmentInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    title = graphene.String()
    event_type = EventType(required=True)
    user_id = GrapheneMongoId(name="user")

    note = graphene.String(required=True)
    is_online = graphene.Boolean(required=True)


class UpdateEventInput(graphene.InputObjectType):
    id_ = GrapheneMongoId(required=True)
    title = graphene.String()
    patients = graphene.List(graphene.NonNull(GrapheneMongoId))
    users = graphene.List(graphene.NonNull(GrapheneMongoId))
    is_online = graphene.Boolean(required=True)
