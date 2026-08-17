from django.urls import path
from .views import (
    register_user,
    login_user,
    user_profile,
    change_password,
    admin_manage_users,
    admin_dashboard_analytics,
    todo_list_create_view,
    todo_detail_view,
    subtodo_create_view,
    subtodo_detail_view,
)

app_name = 'users'

urlpatterns = [
    # Auth & Profile Endpoints
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('profile/', user_profile, name='profile'),
    path('change-password/', change_password, name='change-password'),

    # Admin Control & Analytics Endpoints
    path('admin/users/', admin_manage_users, name='admin-user-list'),
    path('admin/users/<int:user_id>/status/', admin_manage_users, name='admin-user-status'),
    path('admin/analytics/', admin_dashboard_analytics, name='admin-analytics'),
    
    path('todos/', todo_list_create_view, name='todo-list-create'),
    path('todos/<int:todo_id>/', todo_detail_view, name='todo-detail'),
    path('todos/<int:todo_id>/subtasks/', subtodo_create_view, name='subtodo-create'),
    path('subtasks/<int:subtodo_id>/', subtodo_detail_view, name='subtodo-detail'),
]