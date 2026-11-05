from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import Comment, GameComment, Review
import logging

logger = logging.getLogger(__name__)


# --- 1. УВЕДОМЛЕНИЕ О КОММЕНТАРИИ К ОБЗОРУ ---
@receiver(post_save, sender=Comment)
def notify_admin_new_comment(sender, instance, created, **kwargs):
    if not created:
        return

    subject = f'Новый комментарий к обзору: {instance.subject[:50]}'
    admin_link = f'http://127.0.0.1:8000/admin/catalog/comment/{instance.pk}/change/'

    message = (
        f'К обзору "{instance.review.title}"\n'
        f'Автор: {instance.author.username}\n'
        f'Тема: {instance.subject}\n'
        f'Текст: {instance.text}\n'
        f'Модерация: {admin_link}'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email for _, email in settings.ADMINS],
                  fail_silently=False)
        print("!!! ПИСЬМО (ОБЗОР-КОММЕНТ) ОТПРАВЛЕНО!")
    except Exception as e:
        logger.error(f"Ошибка отправки email (обзор-коммент): {e}")


# --- 2. УВЕДОМЛЕНИЕ О КОММЕНТАРИИ К ИГРЕ ---
@receiver(post_save, sender=GameComment)
def notify_admin_new_game_comment(sender, instance, created, **kwargs):
    if not created:
        return

    subject = f'Новый комментарий к игре: {instance.game.title[:50]}'
    link = f'http://127.0.0.1:8000/game/{instance.game.slug}/'

    message = (
        f'Игра: {instance.game.title}\n'
        f'Автор: {instance.author.username}\n'
        f'Текст: {instance.text}\n'
        f'Ссылка: {link}'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email for _, email in settings.ADMINS],
                  fail_silently=False)
        print("!!! ПИСЬМО (ИГРА-КОММЕНТ) ОТПРАВЛЕНО!")
    except Exception as e:
        logger.error(f"Ошибка отправки email (игра-коммент): {e}")


# --- 3. УВЕДОМЛЕНИЕ О НОВОМ ОБЗОРЕ ---
@receiver(post_save, sender=Review)
def notify_admin_new_review(sender, instance, created, **kwargs):
    if not created:
        return

    subject = f'Новый обзор на игру: {instance.game.title[:40]}'
    admin_link = f'http://127.0.0.1:8000/admin/catalog/review/{instance.pk}/change/'

    message = (
        f'Пользователь {instance.author.username} написал обзор.\n\n'
        f'Игра: {instance.game.title}\n'
        f'Заголовок: {instance.title}\n'
        f'Оценка: {instance.rating}/5\n'
        f'Текст: {instance.text[:100]}...\n\n'
        f'Модерация: {admin_link}'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email for _, email in settings.ADMINS],
                  fail_silently=False)
        print("!!! ПИСЬМО (НОВЫЙ ОБЗОР) ОТПРАВЛЕНО!")
    except Exception as e:
        logger.error(f"Ошибка отправки email (обзор): {e}")


# --- 4. УВЕДОМЛЕНИЕ О РЕГИСТРАЦИИ ---
@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    if not created:
        return

    subject = f'Новый пользователь на сайте: {instance.username}'

    message = (
        f'На сайте BoardGamesHub зарегистрировался новый пользователь.\n'
        f'Имя: {instance.username}\n'
        f'Дата: {instance.date_joined}'
    )

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email for _, email in settings.ADMINS],
                  fail_silently=False)
        print("!!! ПИСЬМО (РЕГИСТРАЦИЯ) ОТПРАВЛЕНО!")
    except Exception as e:
        logger.error(f"Ошибка отправки email (регистрация): {e}")