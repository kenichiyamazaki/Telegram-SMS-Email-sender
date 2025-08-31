from django.contrib import admin
from .models import Client, Contact, Notification, NotificationLog

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['contact_type', 'value', 'is_active']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'contacts_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ContactInline]
    
    def contacts_count(self, obj):
        return obj.contacts.count()
    contacts_count.short_description = 'Кол-во контактов'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['client', 'contact_type', 'value', 'is_active', 'created_at']
    list_filter = ['contact_type', 'is_active', 'created_at']
    search_fields = ['client__name', 'value']

class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    extra = 0
    readonly_fields = ['contact', 'status', 'error_message', 'sent_at']
    can_delete = False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'status', 'created_at', 'sent_at']
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'sent_at']
    filter_horizontal = ['clients']
    inlines = [NotificationLogInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'platform')
        }),
        ('Получатели', {
            'fields': ('clients',)
        }),
        ('Время отправки', {
            'fields': ('scheduled_time',)
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'sent_at')
        }),
    )

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'contact', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']
    readonly_fields = ['sent_at']
    search_fields = ['contact__value', 'notification__title']