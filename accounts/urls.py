from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),

    # User management (Manager only)
    path('manage-users/', views.manage_users, name='manage_users'),
    path('create-stockman/', views.create_stockman, name='create_stockman'),
    path('toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('reset-password/<int:user_id>/', views.reset_user_password, name='reset_user_password'),
    path('edit-user/<int:user_id>/', views.edit_user_profile, name='edit_user_profile'),

    # Edit profile (all users)
    path('profile/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_own_password, name='change_own_password'),

    # Notifications API
    path('notifications/', views.notification_list_api, name='notification_list_api'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
]
