from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gql import Address as GqlAddress

from mongoengine import EmbeddedDocument
from mongoengine.fields import StringField, DecimalField


class Address(EmbeddedDocument):
    country = StringField()
    city = StringField()
    address = StringField()
    zipcode = StringField()
    latitude = DecimalField()
    longitude = DecimalField()

    @classmethod
    def from_gql(cls, gql_address: GqlAddress) -> Address:
        return cls(
            address=gql_address.address,
            city=gql_address.city,
            country=gql_address.country,
            zipcode=gql_address.zipcode,
            latitude=gql_address.latitude,
            longitude=gql_address.longitude,
        )
