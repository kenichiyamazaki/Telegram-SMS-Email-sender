from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('send/', views.send_notification, name='send_notification'),
]