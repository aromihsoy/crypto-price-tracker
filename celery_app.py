from celery import Celery
from config import settings




celery_app = Celery(
    "tracker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.beat_schedule = {
    "poll-prices-every-30-seconds": {
        "task": "tasks.poll_and_evaluate",
        "schedule": 30.0,
    },
}

import tasks # noqa