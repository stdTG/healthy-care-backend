from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

from .sex import SexEnum


class PatientUser(BaseModel):
    firstName: str
    lastName: str
    photo: Optional[str]
    birthDate: Optional[date] = "2020-10-12"
    sex: Optional[SexEnum] = SexEnum.UNDEFINED

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    sendSms: Optional[bool] = False
    sendEmail: Optional[bool] = False


class PatientUserInfo(BaseModel):
    firstName: str
    lastName: str
    photo: Optional[str]
    photoContentType: Optional[str]
    birthDate: Optional[date] = "2020-10-12"
    sex: Optional[SexEnum] = SexEnum.UNDEFINED
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class PatientUserUpdate(BaseModel):
    firstName: str
    lastName: str
    birthDate: Optional[date] = "2020-10-12"
    sex: Optional[SexEnum] = SexEnum.UNDEFINED
