import celery

from core.config import get_app_config

__celery_app = None


def get_celery_app():
    global __celery_app
    cfg = get_app_config()

    if not __celery_app:
        __celery_app = celery.Celery("alakine",
                                     # backend=cfg.CELERY_BACKEND_URL,
                                     broker=cfg.CELERY_RABBITMQ_URL)

    return __celery_app
