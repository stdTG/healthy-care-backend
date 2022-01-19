from ..models.care_plan_db import DbCarePlan, DbWidget


def delete_care_plan(id_):
    dbo: DbCarePlan = DbCarePlan.objects.with_id(id_)
    if not dbo:
        return
    dbo.deleted = True
    dbo.save()


def delete_widgets_by_care_plan_id(id_):
    DbWidget.objects(carePlanId=id_).update(set__deleted=True)


async def delete_handler(id_):
    delete_widgets_by_care_plan_id(id_)
    delete_care_plan(id_)
