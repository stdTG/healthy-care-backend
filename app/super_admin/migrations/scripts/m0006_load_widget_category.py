import json

from app.care_plans.models.meta_info_db import Category
from app.patient_info.medical_condition.models.db import MedicalCondition
from app.tenant_workspaces.model_db import Workspace as DbWorkspace, WorkspaceS3Bucket
from core.config import get_app_config
from core.utils.aws import get_s3


async def run():
    cfg = get_app_config()

    log = []

    def init_category():
        categories = [
            "Strength",
            "Endurance",
            "Flexibility",
            "Meditation",
            "Relaxation",
            "Yoga",
            "Pilates",
            "TaiChi",
            "Qi Qong",

        ]
        items = []
        for title in categories:
            item = Category()
            item.title = title

            items.append(item)

        Category.objects.insert(items)

    try:
        init_category()
    except Exception as e:
        log.append(e)
    init_category()

    return log
