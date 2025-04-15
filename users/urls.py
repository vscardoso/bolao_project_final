from django.urls import path
from . import views

app_name = 'users'  # Define o namespace 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
]