from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    """Модель клиента"""
    name = models.CharField(max_length=100, verbose_name='Имя клиента')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
    
    def __str__(self):
        return self.name

class Contact(models.Model):
    """Контактные данные клиента"""
    CONTACT_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('telegram', 'Telegram'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    value = models.CharField(max_length=255, verbose_name='Контакт')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        unique_together = ['contact_type', 'value']
    
    def __str__(self):
        return f"{self.client.name} - {self.get_contact_type_display()}: {self.value}"

class Notification(models.Model):
    """Уведомление для отправки"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланировано'),
        ('processing', 'В процессе'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
    ]
    
    PLATFORM_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('telegram', 'Telegram'),
        ('all', 'Все площадки'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, verbose_name='Площадка')
    clients = models.ManyToManyField(Client, blank=True, verbose_name='Клиенты')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True, verbose_name='Время отправки')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"

class NotificationLog(models.Model):
    """Лог отправки уведомлений"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('success', 'Успешно'), ('failed', 'Ошибка')])
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог отправки'
        verbose_name_plural = 'Логи отправки'
    
    def __str__(self):
        return f"{self.contact} - {self.status}"