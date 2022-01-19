from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..db import Address as DbAddress

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class Address(BaseModel):
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    zipcode: Optional[str]
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]

    @classmethod
    def from_db(cls, db_address: DbAddress) -> Address:
        return cls(
            address=db_address.address,
            city=db_address.city,
            country=db_address.country,
            zipcode=db_address.zipcode,
            latitude=db_address.latitude,
            longitude=db_address.longitude
        )
