from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.web import *
from core.utils.strings import to_camel
from web.core import ObjectIdStr
from .sex import SexEnum


class DashboardUser(BaseModel):
    id: Optional[ObjectIdStr] = None

    # core information
    firstName: str
    middle_name: Optional[str]
    lastName: str
    role: str
    orgUnitId: Optional[ObjectIdStr] = None
    password: Optional[str] = None

    # demographics
    language: Optional[str]
    birthDate: Optional[date]
    sex: SexEnum = SexEnum.UNDEFINED

    # contacts
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[Address]

    # other
    photo: Optional[str]

    class Config:
        alias_generator = to_camel
