import json

from app.care_plans.models.meta_info_db import Prefix
from app.patient_info.medical_condition.models.db import MedicalCondition
from app.tenant_workspaces.model_db import Workspace as DbWorkspace, WorkspaceS3Bucket
from core.config import get_app_config
from core.utils.aws import get_s3


async def run():
    cfg = get_app_config()

    log = []

    def init_prefix():
        prefixes = {
            "mg": "Milligramme",
            "cm": "Centimeter",
            "meter": "Meter",
            "km": "Kilometer",
            "steps": "Steps",
            "mn": "Minutes",
            "h": "Hours",
            "floors": "Floors",
            "kcal": "Calories",
            "dB HL": "Decibels",
            "BPM": "Heart rate",
            "ms": "HRV",
            "%": "Percentage",
            "km/h": "Speed",
            "milliliter": "ml",
            "times": "Times",
            "g/l": "dB HL",
            "Units": "Insulin",
            "s": "Seconds",
            "dia": "Diastolic",
            "sys": "Systolic",
            "C": "Temperature"
        }
        items = []
        for short, full in prefixes.items():
            item = Prefix()
            item.full_title = full
            item.short_title = short

            items.append(item)

        Prefix.objects.insert(items)

    try:
        init_prefix()
    except Exception as e:
        log.append(e)

    return log
