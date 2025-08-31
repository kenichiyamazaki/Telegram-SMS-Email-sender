from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notifications/', include('notification_app.urls')),
    path('', lambda request: redirect('dashboard'), name='home'),
]