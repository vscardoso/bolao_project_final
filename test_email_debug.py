"""
Teste específico de envio de email
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from pools.utils.email import send_welcome_email
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

User = get_user_model()

def test_email_connection():
    """Testa a conexão de email"""
    print("🔧 Testando configurações de email...")
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Teste básico de conexão
    try:
        from django.core.mail import get_connection
        connection = get_connection()
        connection.open()
        print("✅ Conexão SMTP estabelecida com sucesso")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Erro na conexão SMTP: {e}")
        return False

def test_simple_email():
    """Envia um email simples para teste"""
    print("\n📧 Enviando email simples de teste...")
    
    try:
        result = send_mail(
            subject='Teste de Email - Django Bolão',
            message='Este é um email de teste enviado em ' + str(django.utils.timezone.now()),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['***REMOVED***'],  # Enviando para o próprio email
            fail_silently=False,
        )
        print(f"✅ Email simples enviado: {result > 0}")
        return result > 0
    except Exception as e:
        print(f"❌ Erro ao enviar email simples: {e}")
        return False

def test_welcome_email():
    """Testa o email de boas-vindas"""
    print("\n👤 Testando email de boas-vindas...")
    
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado")
        return False
    
    print(f"Usuário: {user.username} ({user.email})")
    
    try:
        result = send_welcome_email(user)
        print(f"✅ Email de boas-vindas enviado: {result}")
        return result
    except Exception as e:
        print(f"❌ Erro ao enviar email de boas-vindas: {e}")
        return False

def main():
    print("🚀 Diagnóstico do Sistema de Email")
    print("=" * 50)
    
    # Teste 1: Configurações
    config_ok = test_email_connection()
    
    # Teste 2: Email simples
    simple_ok = test_simple_email()
    
    # Teste 3: Email HTML complexo
    welcome_ok = test_welcome_email()
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes:")
    print(f"Configuração SMTP: {'✅' if config_ok else '❌'}")
    print(f"Email simples: {'✅' if simple_ok else '❌'}")
    print(f"Email HTML complexo: {'✅' if welcome_ok else '❌'}")
    
    if not any([config_ok, simple_ok, welcome_ok]):
        print("\n🔧 Possíveis soluções:")
        print("1. Verificar senha de app do Gmail")
        print("2. Verificar se 2FA está ativado")
        print("3. Verificar bloqueios do Gmail")
        print("4. Testar com outro provedor SMTP")

if __name__ == "__main__":
    main()