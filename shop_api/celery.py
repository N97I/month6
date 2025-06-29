import os

from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_daily_report": {
        "task": "users.tasks.send_daily_report",
        "schedule": crontab(minute="*/10")
    },
    "send_birthday_greetings": {
        "task": "users.tasks.birthday_cron_task",
        "schedule": crontab(minute=0, hour=9)
    },
}

"""
crontab(minute="*/60") - это то же самое, что crontab(minute=0, hour='*'), т.е. каждый час в 0 минут
crontab(minute=30) - будет запускать задачу каждый час в 30 минут
5 4 * * * - это синтаксис cron для запуска в 4:05 утра каждый день
"""