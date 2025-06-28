from celery import shared_task
from django.core.mail import send_mail
from datetime import date
from .models import CustomUser

@shared_task
def send_otp_email(email, code):
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код: {code}',
        from_email='noreply@example.com',
        recipient_list=[email],
        fail_silently=False,
    )

@shared_task
def send_birthday_email(email, name):
    send_mail(
        subject='С Днём Рождения!',
        message=f'{name}, поздравляем с днём рождения!',
        from_email='noreply@example.com',
        recipient_list=[email],
        fail_silently=False,
    )

@shared_task
def birthday_cron_task():
    today = date.today()
    users = CustomUser.objects.filter(birthday__day=today.day, birthday__month=today.month)
    for user in users:
        send_birthday_email.delay(user.email, user.first_name or user.username)
