"""
URL configuration for bolao_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views as core_views
from users import views as user_views  # Ajuste para o seu app de usuários
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs de autenticação padrão do Django
    path('accounts/', include('django.contrib.auth.urls')),
    
    # URLs personalizadas para recuperação de senha (opcional - apenas se quiser nomes de URLs diferentes)
    path('accounts/password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    path('accounts/password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # URLs de autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', user_views.register, name='register'),
    path('dashboard/', user_views.dashboard, name='dashboard'),  # Redirect direto para o dashboard

    # Outras URLs do projeto
    path('users/', include('users.urls')),
    path('pools/', include('pools.urls', namespace='pools')),
    
    # Inclui todas as URLs do app core também na raiz
    path('', core_views.home, name='home'),
    path('', include('core.urls')),
    
    # Debug toolbar URLs
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
