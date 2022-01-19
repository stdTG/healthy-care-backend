from core.utils.logging import Logger

__logger = Logger()


def get_logger() -> Logger:
    global __logger
    return __logger
