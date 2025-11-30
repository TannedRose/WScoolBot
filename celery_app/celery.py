import os
from celery import Celery
from celery.schedules import crontab

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")

# Создаём экземпляр Celery
celery = Celery(
    "infinitycoin",
    broker=broker_url,
    backend=result_backend,
)

# Настройки
celery.conf.update(
    # Сериализация — поддержка Decimal
    result_serializer="json",
    task_serializer="json",
    accept_content=["json"],
    result_backend_transport_options={
        "json_encoder": "celery_app.utils.DecimalEncoder",
        "json_decoder": "json.JSONDecoder",
    },
    # Расписание (beat)
    beat_schedule={
        'notification': {
            'task': 'celery_app.tasks.send_notification',
            'schedule': crontab(hour="8", minute='0'),
        },
        'query': {
            'task': 'celery_app.tasks.query_user',
            'schedule': crontab(hour="20", minute='0'),
        },
    },
    timezone="Europe/Minsk",
    enable_utc=False,
    include=["celery_app.tasks"],
)