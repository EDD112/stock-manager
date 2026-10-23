from django.urls import path
from . import views

urlpatterns = [
    path('', views.expiration_tracker, name='expiration_tracker'),
]
