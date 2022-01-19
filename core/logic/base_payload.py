import functools
import math

import graphene
from graphene import Mutation
from graphene.utils.get_unbound_function import get_unbound_function
from mongoengine.errors import NotUniqueError, ValidationError

from core.utils.logging import Logger
from ..errors import ErrorInterface, ServerGqlError, TitleAlreadyTakenGqlError, ValidationGqlError

__logger = Logger()


def wrap_resolver(cls, resolver):
    @functools.wraps(resolver)
    async def wrapped_resolver(root, info, **args):
        try:
            res = await resolver(root, info, **args)
            return res
        except ValidationError as e:
            __logger.error(e)
            if e.errors:
                for field_name, error in e.errors.items():
                    return cls(error=ValidationGqlError(path=field_name, message=error.message))
            return cls(error=ValidationGqlError(path=e.field_name, message=e.args[0]))

        except NotUniqueError as e:
            return cls(error=TitleAlreadyTakenGqlError(message="Something field is not unique"))
        except Exception as e:
            __logger.error(e)
            return cls(error=ServerGqlError())

    return wrapped_resolver


class MutationPayload(Mutation):
    class Meta:
        abstract = True

    ok = graphene.Boolean()
    error = graphene.Field(ErrorInterface)
    query = graphene.Field("web.startup.graphql.Queries")

    @classmethod
    def __init_subclass_with_meta__(cls, resolver=None, **options):
        if not resolver:
            mutate = getattr(cls, 'mutate', None)
            assert mutate, 'All mutations must define a mutate method in it'
            resolver = wrap_resolver(cls, mutate)
            resolver = get_unbound_function(resolver)

        super(MutationPayload, cls).__init_subclass_with_meta__(resolver=resolver, **options)

    def resolve_ok(self, _):
        return not self.error

    def resolve_error(self, _):
        return self.error

    def resolve_query(self, _):
        return {}


class PaginationInfo(graphene.ObjectType):
    def __init__(self, page, per_page, total_items, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_items = total_items
        self.page = page
        self.per_page = per_page
        self.total_pages = math.ceil(self.total_items / self.per_page)
        self.has_next_page = self.page < self.total_pages - 1
        self.has_previous_page = 0 < self.page <= self.total_pages - 1

    # Total number of pages
    total_pages = graphene.Int()
    # Total number of items
    total_items = graphene.Int()
    # Current page number
    page = graphene.Int()
    # Number of items per page
    per_page = graphene.Int()
    # When paginating forwards, are there more items?
    has_next_page = graphene.Int(required=True)
    # When paginating backwards, are there more items?
    has_previous_page = graphene.Int(required=True)
