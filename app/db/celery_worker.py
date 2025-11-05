from celery import Celery
from celery.schedules import crontab

from app.core.app import app_settings

celery_app = Celery(
    "quiz_app",
    broker=app_settings.redis.url,
    backend=app_settings.redis.url,
    include=["app.tasks.quiz"],
)

celery_app.conf.beat_schedule = {
    "check-quizzes-every-day": {
        "task": "app.tasks.quiz",
        "schedule": crontab(hour=0, minute=0),
    },
}

celery_app.conf.timezone = "Europe/Bratislava"
