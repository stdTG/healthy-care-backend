import graphene


class PageInfo(graphene.ObjectType):
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


def create_paged_list(item_type):
    class PagedListBase(graphene.ObjectType):
        page_info = graphene.Field(PageInfo)

    class_name = f"{item_type.__name__}_PagedList_FromFactory"

    new_class = type(class_name, (PagedListBase,), {
        "items": graphene.List(item_type)
    })

    PagedListField = lambda **kwargs: graphene.Field(
        new_class,
        **kwargs,
        page=graphene.Int(required=True, default_value=0),
        per_page=graphene.Int(required=True, default_value=100)
    )

    return new_class, PagedListField, PageInfo
