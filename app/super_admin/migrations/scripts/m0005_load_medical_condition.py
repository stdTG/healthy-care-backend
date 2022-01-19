import json

from app.patient_info.medical_condition.models.db import MedicalCondition
from app.tenant_workspaces.model_db import Workspace as DbWorkspace, WorkspaceS3Bucket
from core.config import get_app_config
from core.utils.aws import get_s3


async def run():
    cfg = get_app_config()

    log = []

    def init_medical_conditions():
        med_conds = [
            "Covid-19",
            "Flu",
            "Pregnancy",
            "Astma",
        ]
        items = []
        for name in med_conds:
            item: MedicalCondition = MedicalCondition()
            item.name = name

            items.append(item)

        MedicalCondition.objects.insert(items)

    init_medical_conditions()

    return log
