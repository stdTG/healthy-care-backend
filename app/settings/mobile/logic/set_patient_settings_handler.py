import app.settings.models.db as dbm
import app.settings.models.web as webm

from . import init_settings


async def run(web_object: webm.PatientSettings, current_user_sub: str):
    settings: dbm.PatientSettings = dbm.PatientSettings.objects(cognitoSub=current_user_sub).first()

    if not settings:
        settings = await init_settings.run(current_user_sub)

    settings.weightUnit = web_object.weightUnit
    settings.distanceUnit = web_object.distanceUnit
    settings.temperatureUnit = web_object.temperatureUnit

    settings.remindersNotification = web_object.remindersNotification
    settings.appointmentsNotification = web_object.appointmentsNotification
    settings.messagesNotification = web_object.messagesNotification

    settings.language = web_object.language

    settings.save()
    return "Settings successfully saved"
