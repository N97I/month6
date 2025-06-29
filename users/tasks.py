from celery import shared_task
from django.core.mail import send_mail
from datetime import date
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_otp_email(self, email, confirmation_code):
    """
    Отправляет код подтверждения (OTP) на указанный email через SMTP.
    """
    logger.info(f"Начинаем отправку OTP-письма на адрес: {email}")
    try:
        send_mail(
            subject='Ваш код подтверждения для регистрации',
            message=f'Здравствуйте!\n\nВаш код подтверждения: {confirmation_code}\n\nПожалуйста, используйте этот код, чтобы завершить регистрацию на нашем сайте.',
            from_email='gjake3848@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"OTP-письмо успешно отправлено на адрес: {email}")
    except Exception as exc:
        logger.error(f"Не удалось отправить OTP-письмо на адрес {email}: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True)
def send_birthday_email(self, email, name):
    """
    Отправляет поздравительное письмо с днем рождения указанному пользователю.
    """
    logger.info(f"Начинаем отправку поздравительного письма для: {email} ({name})")
    try:
        send_mail(
            subject='С Днём Рождения!',
            message=f'Дорогой(ая) {name},\n\nКоманда нашего магазина искренне поздравляет вас с днём рождения! Желаем вам счастья, здоровья и успехов во всём!\n\nС наилучшими пожеланиями,\nВаш Shop API.',
            from_email='gjake3848@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Поздравительное письмо с днем рождения успешно отправлено пользователю: {email} ({name})")
    except Exception as exc:
        logger.error(f"Не удалось отправить поздравительное письмо с днем рождения пользователю {email} ({name}): {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task
def birthday_cron_task():
    """
    Запланированная задача, которая ищет пользователей с днем рождения сегодня
    и отправляет им поздравительные письма.
    Эта задача будет запускаться с помощью Celery Beat.
    """
    logger.info("Запущена задача birthday_cron_task...")
    today = date.today()
    users = CustomUser.objects.filter(birthday__day=today.day, birthday__month=today.month)
    
    if not users.exists():
        logger.info(f"Пользователей с днем рождения {today.strftime('%d.%m')} не найдено.")
        return

    for user in users:
        send_birthday_email.delay(user.email, user.first_name or user.username)
        logger.info(f"Запланирована отправка поздравительного письма для {user.email} ({user.first_name or user.username}).")
    
    logger.info("Задача birthday_cron_task завершена.")


@shared_task
def send_daily_report():
    """
    Заглушка для задачи отправки ежедневного отчета.
    Заполните эту функцию логикой для генерации и отправки вашего отчета.
    """
    logger.info("Запущена задача send_daily_report...")

    
    logger.info("Задача send_daily_report завершена (пока это только заглушка).")