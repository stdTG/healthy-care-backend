from web.cloudauth.auth import Authorization

__auth = Authorization()


def get_current_auth() -> Authorization:
    global __auth
    return __auth
