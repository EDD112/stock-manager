from django.urls import path
from . import views

urlpatterns = [
    path('',              views.login_activity_list,  name='login_activity'),
    path('clear/',        views.clear_login_activity, name='clear_login_activity'),
    path('export/excel/', views.export_login_excel,   name='export_login_excel'),
    path('export/pdf/',   views.export_login_pdf,     name='export_login_pdf'),
    path('search/',       views.live_search_login,     name='live_search_login'),
]
