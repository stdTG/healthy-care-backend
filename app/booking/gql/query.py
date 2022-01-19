import datetime
from typing import List

import graphene
from graphql import GraphQLError
from mongoengine import Q

from app.context import get_current_auth, get_current_master_org, get_user
from app.users.common.models.db import DashboardUser
from core.errors import ErrorEnum
from core.logic.base_payload import PaginationInfo
from .inputs import FilterFindManyAppointment, FilterFindManyTimeSlot
from .payloads import EventAndAppointmentPayload, EventPagination, TimeslotPayload
from ..logic import get_free_timeslots_for_day
from ..models.db import Appointment as DbAppointment
from ..models.gql import Appointment as GqlAppointment, Event


class ScheduleQueries(graphene.ObjectType):
    event_many = graphene.Field(
        type=EventAndAppointmentPayload,
        filter=FilterFindManyAppointment(required=True),
    )
    event_pagination = graphene.Field(
        type=EventPagination,
        page=graphene.Int(required=True),
        per_page=graphene.Int(required=True),
        filter_=FilterFindManyAppointment(required=True, name="filter"),
    )
    timeslot_many = graphene.Field(
        type=TimeslotPayload,
        filter=FilterFindManyTimeSlot(required=True),
    )
    appointment_by_id = graphene.Field(GqlAppointment, id_=graphene.ID(required=True))
    event_by_id = graphene.Field(Event, id_=graphene.ID(required=True))

    async def resolve_appointment_by_id(self, info, id_):
        appointment: DbAppointment = DbAppointment.objects.with_id(id_)
        if appointment.isAppointment:
            return GqlAppointment.from_db(appointment)

    async def resolve_event_by_id(self, info, id_):
        appointment: DbAppointment = DbAppointment.objects.with_id(id_)
        if not appointment:
            return Event.from_db(appointment)

    async def resolve_timeslot_many(self, info, **kwargs):
        filter_: FilterFindManyTimeSlot = kwargs.get("filter")
        request = info.context['request']
        master_org = await get_current_master_org(request)
        if filter_.user:
            user: DashboardUser = DashboardUser.objects.with_id(filter_.user)
        else:
            auth = await get_current_auth(request)
            user: DashboardUser = DashboardUser.objects(cognito_sub=auth.sub).first()

        time_slots = await get_free_timeslots_for_day(user, master_org, filter_.date)
        return TimeslotPayload(items=time_slots)

    async def resolve_event_many(self, info, **kwargs):
        filter_: FilterFindManyAppointment = kwargs.get("filter")
        filter_.end_date = filter_.end_date + datetime.timedelta(days=1)
        result = []

        # if not filter_.user:
        #     user = await get_user(info)
        #     if not user:
        #         return EventAndAppointmentPayload(items=result)
        #
        #     filter_.user = user.id

        queryset = DbAppointment.objects \
            .filter(
            (Q(startDate__gte=filter_.start_date) & Q(startDate__lte=filter_.end_date)) |
            (Q(endDate__gte=filter_.start_date) & Q(endDate__lte=filter_.end_date))
        )

        if filter_.user:
            queryset = queryset \
                .filter(users__id=str(filter_.user)
            )
        elif not filter_.user:
            user = await get_user(info)
            if user.orgUnitId:
                users = DashboardUser.objects \
                    .filter(orgUnitId=user.orgUnitId, deleted=False).all()

                queryset = queryset.filter(users__id__in=[user.id for user in users])
            else:
                queryset = queryset.filter(users__id=user.id)

        if filter_.patient:
            queryset = queryset \
                .filter(
                Q(patients__id=filter_.patient)
            )

        appointments: List[DbAppointment] = queryset \
            .order_by('startDate') \
            .all()

        for i in appointments:
            if i.isAppointment:
                result.append(GqlAppointment.from_db(i))
            else:
                result.append(Event.from_db(i))

        return EventAndAppointmentPayload(items=result)

    async def resolve_event_pagination(self, info, page: int, per_page: int, filter_):
        if page < 0:
            raise GraphQLError(
                message="Argument `page` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        if per_page <= 0:
            raise GraphQLError(
                message="Argument `perPage` should be positive number.",
                extensions={"code": ErrorEnum.GRAPHQL_VALIDATION_FAILED},
            )
        queryset = DbAppointment.objects

        if filter_.start_date:
            queryset = queryset \
                .filter(
                (Q(startDate__gte=filter_.start_date)) |
                (Q(endDate__gte=filter_.start_date))
            )
        if filter_.end_date:

            queryset = queryset \
                .filter(
                (Q(startDate__lte=filter_.end_date)) |
                (Q(endDate__lte=filter_.end_date))
            )
        if filter_.start_date:
            queryset = queryset \
                .filter(
                (Q(startDate__gte=filter_.start_date) & Q(startDate__lte=filter_.end_date)) |
                (Q(endDate__gte=filter_.start_date) & Q(endDate__lte=filter_.end_date))
            )

        if filter_.user_id:
            queryset = queryset \
                .filter(
                Q(users__match={"id": filter_.user_id, })
            )

        if filter_.patient:
            queryset = queryset \
                .filter(
                Q(patients__id=filter_.patient)
            )

        count = queryset.count()
        appointments = queryset \
            .skip(page * per_page) \
            .limit(per_page) \
            .order_by('-startDate') \
            .all()

        result = []
        for i in appointments:
            if i.isAppointment:
                result.append(GqlAppointment.from_db(i))
            else:
                result.append(Event.from_db(i))

        pagination = EventPagination()
        pagination_info = PaginationInfo(page=page, per_page=per_page, total_items=count)
        pagination.page_info = pagination_info
        pagination.items = result

        return pagination
