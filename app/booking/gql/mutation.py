import graphene

from app.context import get_current_master_org, get_user
from app.users.common.models.db import DashboardUser as DbDashboardUser
from app.users.common.models.gql import DashboardUser as GqlUser
from core.errors import NotAvailableGqlError, NotFoundGqlError
from core.logic.base_payload import MutationPayload
from .inputs import (AppointmentCreateInput, EventCreateInput, RescheduleAppointmentInput,
                     RescheduleEventInput,
                     UpdateAppointmentInput, UpdateEventInput)
from .payloads import NotAvailableErrorExtend
from ..logic import is_timeslot_free
from ..logic.utils import get_appointments_in_dates
from ..models.db import Appointment as DbAppointment, AppointmentStatus
from ..models.gql import Appointment as GqlAppointment, Event
from ...org_units.model_db import OrgUnit


class CreateAppointment(MutationPayload):
    """Mutation to create appointment."""

    class Arguments:
        record = AppointmentCreateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlAppointment)

    async def mutate(self, info, record: AppointmentCreateInput):
        request = info.context["request"]

        user: DbDashboardUser = DbDashboardUser.objects.with_id(record.user) if record.user \
            else (await get_user(info))

        if not await is_timeslot_free(user.id, record.start_date, record.end_date):
            return CreateAppointment(error=NotAvailableGqlError())

        location = None if record.is_online else (await get_org_unit_for_user(user, request)).id
        db_appointment = DbAppointment.from_gql_appointment(record, user.id, location)
        db_appointment.save()

        return CreateAppointment(result_id=db_appointment.id,
                                 result=GqlAppointment.from_db(db_appointment))


class CreateEvent(MutationPayload):
    """Mutation to create event."""

    class Arguments:
        record = EventCreateInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(Event)
    error = graphene.Field(NotAvailableErrorExtend)

    async def mutate(self, info, record: EventCreateInput):
        request = info.context["request"]
        user = await get_user(info)

        not_free_users = []
        users = DbDashboardUser.objects.filter(pk__in=record.users, deleted=False).all()
        for user in users:
            if not await is_timeslot_free(user.id, record.start_date, record.end_date):
                not_free_users.append(user)

        if not_free_users:
            return CreateEvent(
                error=NotAvailableErrorExtend(users=[GqlUser.from_db(user) for user in not_free_users]))

        location = None if record.is_online else (await get_org_unit_for_user(user, request)).id
        event = DbAppointment.from_gql_event(record, user.id, location)
        event.save()

        return CreateEvent(result_id=event.id, result=Event.from_db(event))


class CancelAppointment(MutationPayload):
    """Mutation to cancel appointment by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlAppointment)

    async def mutate(self, info, id_):
        appointment: DbAppointment = DbAppointment.objects.with_id(id_)
        if appointment:
            appointment.users[0].status = AppointmentStatus.CANCELLED
            appointment.patients[0].status = AppointmentStatus.CANCELLED
            appointment.save()

        return CancelAppointment(result_id=appointment.id,
                                 result=GqlAppointment.from_db(appointment))


class RescheduleAppointment(MutationPayload):
    """Mutation to reschedule appointment by id."""

    class Arguments:
        record = RescheduleAppointmentInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlAppointment)

    async def mutate(self, _, record: RescheduleAppointmentInput):
        appointment: DbAppointment = DbAppointment.objects.with_id(record.id_)
        if not appointment:
            return RescheduleAppointment(NotFoundGqlError())

        if appointment.startDate == record.start_date and appointment.endDate == record.end_date:
            return RescheduleAppointment(result_id=appointment.id,
                                         result=GqlAppointment.from_db(appointment))

        user: DbDashboardUser = DbDashboardUser.objects.with_id(appointment.users[0].id)
        if not await is_timeslot_free(user.id, record.start_date, record.end_date):
            return RescheduleAppointment(error=NotAvailableGqlError())

        appointment.startDate = record.start_date
        appointment.endDate = record.end_date
        appointment.patients[0].status = AppointmentStatus.AWAITING
        appointment.save()

        return RescheduleAppointment(result_id=appointment.id,
                                     result=GqlAppointment.from_db(appointment))


class UpdateAppointment(MutationPayload):
    """Mutation to update appointment by id."""

    class Arguments:
        record = UpdateAppointmentInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(GqlAppointment)

    async def mutate(self, info, record: UpdateAppointmentInput):
        request = info.context["request"]

        appointment: DbAppointment = DbAppointment.objects.with_id(record.id_)
        if not appointment:
            return UpdateAppointment(error=NotFoundGqlError())

        user: DbDashboardUser = DbDashboardUser.objects.with_id(record.user_id)
        if not user:
            return UpdateAppointment(error=NotFoundGqlError())

        if appointment.users[0].id != record.user_id:
            start_date = appointment.startDate
            end_date = appointment.endDate

            if not await is_timeslot_free(user.id, start_date, end_date):
                return UpdateAppointment(error=NotAvailableGqlError())

            appointment.users[0].id = user.id

        if appointment.location and record.is_online:
            appointment.location = None
        elif not (appointment.location and record.is_online):
            appointment.location = (await get_org_unit_for_user(user, request)).id

        appointment.title = record.title
        appointment.eventType = record.event_type
        appointment.note = record.note

        appointment.patients[0].status = AppointmentStatus.AWAITING
        appointment.save()

        return UpdateAppointment(result_id=appointment.id,
                                 result=GqlAppointment.from_db(appointment))


class CancelEvent(MutationPayload):
    """Mutation to cancel Event by id."""

    class Arguments:
        id_ = graphene.ID(required=True)

    result_id = graphene.ID()
    result = graphene.Field(Event)

    async def mutate(self, info, id_):
        event: DbAppointment = DbAppointment.objects.with_id(id_)
        if not event:
            return CancelEvent(NotFoundGqlError())

        for user in event.users:
            user.status = AppointmentStatus.CANCELLED

        for patient in event.patients:
            patient.status = AppointmentStatus.CANCELLED

        event.save()

        return CreateEvent(result_id=event.id, result=Event.from_db(event))


class UpdateEvent(MutationPayload):
    """Mutation to update event by id."""

    class Arguments:
        record = UpdateEventInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(Event)

    async def mutate(self, info, record: UpdateEventInput):
        request = info.context["request"]

        event: DbAppointment = DbAppointment.objects.with_id(record.id_)
        if not event:
            return UpdateEvent(NotFoundGqlError())

        event.title = record.title

        if event.location and record.is_online:
            event.location = None
        elif not (event.location and record.is_online):
            user: DbDashboardUser = DbDashboardUser.objects.with_id(event.createdById)
            event.location = (await get_org_unit_for_user(user, request)).id

        event.patients = DbAppointment.create_statuses(record.patients, AppointmentStatus.AWAITING)
        event.users = DbAppointment.create_statuses(record.users, AppointmentStatus.AWAITING)

        event.save()
        return UpdateEvent(result_id=event.id, result=Event.from_db(event))


class SubmitEvent(MutationPayload):
    """Mutation to update event by id.
    it cancels all appointments on the given times."""

    class Arguments:
        id_ = graphene.ID(required=True)

    result_id = graphene.ID()
    result = graphene.Field(Event)

    async def mutate(self, info, id_):
        event: DbAppointment = DbAppointment.objects.with_id(id_)
        if not event:
            return SubmitEvent(NotFoundGqlError())

        user: DbDashboardUser = await get_user(info)
        apps = await get_appointments_in_dates(user.id, event.startDate, event.endDate)
        for app in apps:
            for curr_user in app.users:
                if user.id == curr_user.id:
                    curr_user.status = AppointmentStatus.CANCELLED
            if len(app.users) == 1:
                for curr_patient in app.patients:
                    curr_patient.status = AppointmentStatus.CANCELLED

            app.save()

        status_info = list(filter(lambda st_i: st_i.user_id == user.id, event.users))
        if status_info:
            status_info[0].status = AppointmentStatus.APPROVED

        event.save()

        return SubmitEvent(result_id=event.id, result=Event.from_db(event))


class RescheduleEvent(MutationPayload):
    """Mutation to reschedule event by id."""

    class Arguments:
        record = RescheduleEventInput(required=True)

    result_id = graphene.ID()
    result = graphene.Field(Event)

    async def mutate(self, info, record: RescheduleEventInput):
        event: DbAppointment = DbAppointment.objects.with_id(record.id_)
        if not event:
            return RescheduleEvent(NotFoundGqlError())

        event.startDate = record.start_date
        event.endDate = record.end_date

        for status_info in event.patients + event.users:
            status_info.status = AppointmentStatus.AWAITING

        event.save()

        return RescheduleEvent(result_id=event.id, result=Event.from_db(event))


async def get_org_unit_for_user(user: DbDashboardUser, request) -> OrgUnit:
    if user.orgUnitId:
        org_unit: OrgUnit = OrgUnit.objects.with_id(user.orgUnitId)
        if not org_unit.isCareTeam:
            return org_unit

        elif org_unit.isCareTeam and org_unit.parentId:
            sub_org: OrgUnit = OrgUnit.objects.with_id(user.orgUnitId)
            return sub_org

        elif org_unit.isCareTeam and not org_unit.parentId:
            master_org = await get_current_master_org(request)
            return master_org

    else:
        master_org = await get_current_master_org(request)
        return master_org


class ScheduleMutations(graphene.Mutation):
    create_event = CreateEvent.Field()
    cancel_event = CancelEvent.Field()
    update_event = UpdateEvent.Field()
    submit_event = SubmitEvent.Field()
    reschedule_event = RescheduleEvent.Field()
    create_appointment = CreateAppointment.Field()
    cancel_appointment = CancelAppointment.Field()
    reschedule_appointment = RescheduleAppointment.Field()
    update_appointment = UpdateAppointment.Field()

    async def mutate(self, _):
        return {}
