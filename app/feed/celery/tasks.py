import app.feed.celery.start
import app.feed.celery.stop
from core.factory.celery import get_celery_app

capp = get_celery_app()


@capp.task(name="feed.start")
def start(*args, **kwargs):
    app.feed.celery.start.run(*args, **kwargs)


@capp.task(name="feed.stop")
def stop(*args, **kwargs):
    app.feed.celery.stop.run(*args, **kwargs)
