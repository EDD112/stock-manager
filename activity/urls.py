from django.urls import path
from . import views

urlpatterns = [
    path('',              views.activity_log,         name='activity_log'),
    path('clear/',        views.clear_activity_logs,  name='clear_activity_logs'),
    path('export/excel/', views.export_activity_excel, name='export_activity_excel'),
    path('export/pdf/',   views.export_activity_pdf,   name='export_activity_pdf'),
    path('search/',        views.live_search_activity,   name='live_search_activity'),
]
