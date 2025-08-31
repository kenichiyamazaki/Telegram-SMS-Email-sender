from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import NotificationForm
from .models import Notification
from .tasks import send_notification_task

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Главная страница со статистикой"""
    notifications = Notification.objects.all().order_by('-created_at')[:9]
    total_notifications = Notification.objects.count()
    sent_notifications = Notification.objects.filter(status='completed').count()
    
    context = {
        'notifications': notifications,
        'total_notifications': total_notifications,
        'sent_notifications': sent_notifications,
    }
    return render(request, 'notification_app/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def send_notification(request):
    """Страница отправки уведомления"""
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.created_by = request.user
            
            if notification.scheduled_time:
                notification.status = 'scheduled'
            else:
                notification.status = 'draft'
            
            notification.save()
            form.save_m2m()  # Сохраняем ManyToMany отношения
            
            # Запускаем задачу отправки
            if not notification.scheduled_time:
                send_notification_task.delay(notification.id)
                messages.success(request, 'Уведомление поставлено в очередь на отправку!')
            else:
                messages.success(request, 'Уведомление запланировано на отправку!')
            
            return redirect('dashboard')
    else:
        form = NotificationForm()
    
    return render(request, 'notification_app/send_notification.html', {'form': form})