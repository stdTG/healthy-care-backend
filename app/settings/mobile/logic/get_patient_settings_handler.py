import app.settings.models.db as dbm
import app.settings.models.web as webm

from . import init_settings


async def run(current_user_sub: str):
    settings: dbm.PatientSettings = dbm.PatientSettings.objects(cognitoSub=current_user_sub).first()

    if not settings:
        settings = await init_settings.run(current_user_sub)

    return webm.PatientSettings(
        weightUnit=settings.weightUnit,
        distanceUnit=settings.distanceUnit,
        temperatureUnit=settings.temperatureUnit,

        remindersNotification=settings.remindersNotification,
        appointmentsNotification=settings.appointmentsNotification,
        messagesNotification=settings.messagesNotification,

        language=settings.language,
    )
