import time
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .models import Notification, Contact, NotificationLog

@shared_task
def send_notification_task(notification_id):
    """Основная задача для отправки уведомления"""
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.status = 'processing'
        notification.save()
        
        # Получаем контакты для рассылки
        contacts = Contact.objects.filter(
            client__in=notification.clients.all(),
            contact_type=notification.platform if notification.platform != 'all' else None,
            is_active=True
        )
        
        if notification.platform == 'all':
            contacts = Contact.objects.filter(
                client__in=notification.clients.all(),
                is_active=True
            )
        
        success_count = 0
        fail_count = 0
        
        for contact in contacts:
            try:
                if contact.contact_type == 'email':
                    send_email(contact.value, notification.title, notification.message)
                elif contact.contact_type == 'sms':
                    send_sms(contact.value, notification.message)
                elif contact.contact_type == 'telegram':
                    send_telegram(contact.value, notification.message)
                
                # Логируем успешную отправку
                NotificationLog.objects.create(
                    notification=notification,
                    contact=contact,
                    status='success'
                )
                success_count += 1
                
            except Exception as e:
                # Логируем ошибку
                NotificationLog.objects.create(
                    notification=notification,
                    contact=contact,
                    status='failed',
                    error_message=str(e)
                )
                fail_count += 1
            
            # Небольшая задержка между отправками, чтобы не отправлялось в спам
            time.sleep(0.1)
        
        # Обновляем статус уведомления
        notification.status = 'completed'
        notification.sent_at = timezone.now()
        notification.save()
        
        return f"Уведомление отправлено. Успешно: {success_count}, Ошибок: {fail_count}"
        
    except Notification.DoesNotExist:
        return "Уведомление не найдено"
    except Exception as e:
        notification.status = 'failed'
        notification.save()
        return f"Ошибка при отправке: {str(e)}"

def send_email(to_email, subject, message):
    """Отправка email через Django Email Backend"""
    print("DEBUG:", settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    print(f"[EMAIL] Отправка на {to_email}: {subject}")
    print(f"Сообщение: {message}")

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [to_email],
            fail_silently=False,
        )
        print(f"Email отправлен на {to_email}")

    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        raise

def send_sms(phone_number, message):
    """Отправка SMS (заглушка с имитацией)"""
    print(f"[SMS] Отправка на {phone_number}")
    print(f"Сообщение: {message}")
    
    # Имитация отправки SMS
    if hasattr(settings, 'SMS_ACCOUNT_SID'):
        # Реальная отправка через Twilio
        try:
            # from twilio.rest import Client
            # client = Client(settings.SMS_ACCOUNT_SID, settings.SMS_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.SMS_FROM_NUMBER,
            #     to=phone_number
            # )
            print(f"SMS отправлено на {phone_number}")
            
        except Exception as e:
            print(f"Ошибка отправки SMS: {e}")
            raise
    else:
        # Заглушка для демонстрации
        print(f"Имитация отправки SMS на {phone_number}")

def send_telegram(chat_id, message):
    """Отправка в Telegram (заглушка с имитацией)"""
    print(f"[TELEGRAM] Отправка для chat_id {chat_id}")
    print(f"Сообщение: {message}")
    
    # Реальная отправка через Telegram Bot API
    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"Telegram сообщение отправлено для chat_id {chat_id}")
            
    except Exception as e:
        print(f"Ошибка отправки Telegram: {e}")
        raise