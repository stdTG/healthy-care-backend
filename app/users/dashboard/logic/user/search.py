from mongoengine import Q, QuerySet

from app.users.dashboard.logic.utils import create_regexp


def search_users(name: str, users_queryset: QuerySet):
    name = name.strip()

    if " " in name:
        f_name, s_name = name.split(" ", 1)
        f_name_regex = create_regexp(f_name.strip())
        s_name_regex = create_regexp(s_name.strip())

        full_match_users_queryset = users_queryset.filter(
            (Q(firstName=f_name_regex) & Q(lastName=s_name_regex)) |
            (Q(firstName=s_name_regex) & Q(lastName=f_name_regex))
        )

        if len(full_match_users_queryset) == 0:
            users_queryset = users_queryset.filter(
                Q(firstName=f_name_regex) | Q(firstName=s_name_regex) |
                Q(lastName=f_name_regex) | Q(lastName=s_name_regex)
            )
        else:
            users_queryset = full_match_users_queryset
    else:
        name_regex = create_regexp(name)
        users_queryset = users_queryset.filter(
            Q(firstName=name_regex) | Q(lastName=name_regex)
        )

    return users_queryset
