from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'  # Define o namespace 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.SignupView.as_view(), name='signup'),
]