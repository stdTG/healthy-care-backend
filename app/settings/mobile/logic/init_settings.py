import app.settings.models.db as dbm
import app.users.common.models.db as users_dbm
from core.errors import HTTPNotFoundError


async def run(current_user_sub: str):
    db_patient: users_dbm.PatientUser = users_dbm.PatientUser.objects(
        cognito_sub=current_user_sub).first()

    if not db_patient:
        raise HTTPNotFoundError(message=f"Patient not found [{current_user_sub}]")

    settings = dbm.PatientSettings(
        patientId=str(db_patient.id),
        cognitoSub=current_user_sub
    )
    settings.save()

    return settings
