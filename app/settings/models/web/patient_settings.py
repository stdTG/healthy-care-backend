from typing import List

from pydantic import BaseModel

from app.measurement_units.models.web import UnitWeight, UnitDistance, UnitTemperature
from .language import Language
from .notification_type import NotificationType


class PatientSettings(BaseModel):
    weightUnit: UnitWeight = UnitWeight.kg
    distanceUnit: UnitDistance = UnitDistance.metric
    temperatureUnit: UnitTemperature = UnitTemperature.celsius

    remindersNotification: List[NotificationType]
    appointmentsNotification: List[NotificationType]
    messagesNotification: List[NotificationType]

    language: Language = Language.english
