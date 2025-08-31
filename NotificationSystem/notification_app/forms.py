from django import forms
from .models import Notification, Client

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'platform', 'clients', 'scheduled_time']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите текст сообщения...'}),
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clients': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
        labels = {
            'title': 'Заголовок уведомления',
            'message': 'Текст сообщения',
            'platform': 'Площадка для отправки',
            'clients': 'Клиенты для рассылки',
            'scheduled_time': 'Время отправки (необязательно)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clients'].queryset = Client.objects.all()
        self.fields['clients'].initial = Client.objects.all().values_list('id', flat=True)
        self.fields['scheduled_time'].required = False