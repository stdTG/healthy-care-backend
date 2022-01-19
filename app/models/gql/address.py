from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..db import Address as DbAddress

import graphene


class Address(graphene.ObjectType):
    country = graphene.String()
    city = graphene.String()
    address = graphene.String()
    zipcode = graphene.String()
    latitude = graphene.Decimal()
    longitude = graphene.Decimal()

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


class AddressInput(graphene.InputObjectType):
    country = graphene.String()
    city = graphene.String()
    address = graphene.String()
    zipcode = graphene.String()
    latitude = graphene.Decimal()
    longitude = graphene.Decimal()
