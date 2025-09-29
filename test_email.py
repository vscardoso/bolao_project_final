#!/usr/bin/env python3
"""
Script para testar configuração de email Gmail no Django Bolão
Verifica se o SMTP está funcionando corretamente

Autor: Sistema Django Bolão
Data: 29/09/2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Configurar caminho do Django
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')

# Inicializar Django
import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend


def check_email_settings():
    """Verifica as configurações de email"""
    print("⚙️ VERIFICAÇÃO DE CONFIGURAÇÕES")
    print("-" * 40)
    
    settings_to_check = [
        ('EMAIL_BACKEND', getattr(settings, 'EMAIL_BACKEND', 'NÃO CONFIGURADO')),
        ('EMAIL_HOST', getattr(settings, 'EMAIL_HOST', 'NÃO CONFIGURADO')),
        ('EMAIL_PORT', getattr(settings, 'EMAIL_PORT', 'NÃO CONFIGURADO')),
        ('EMAIL_HOST_USER', getattr(settings, 'EMAIL_HOST_USER', 'NÃO CONFIGURADO')),
        ('EMAIL_HOST_PASSWORD', '****** (protegida)' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NÃO CONFIGURADO'),
        ('EMAIL_USE_TLS', getattr(settings, 'EMAIL_USE_TLS', 'NÃO CONFIGURADO')),
        ('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'NÃO CONFIGURADO')),
    ]
    
    all_configured = True
    for setting_name, setting_value in settings_to_check:
        status = "✅" if str(setting_value) != "NÃO CONFIGURADO" else "❌"
        print(f"{status} {setting_name}: {setting_value}")
        if str(setting_value) == "NÃO CONFIGURADO":
            all_configured = False
    
    print()
    return all_configured


def test_smtp_connection():
    """Testa conexão SMTP sem enviar email"""
    print("🔌 TESTE DE CONEXÃO SMTP")
    print("-" * 30)
    
    try:
        backend = EmailBackend(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        # Tentar abrir conexão
        connection = backend.open()
        if connection:
            print("✅ Conexão SMTP estabelecida com sucesso!")
            backend.close()
            return True
        else:
            print("❌ Falha ao estabelecer conexão SMTP")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão SMTP: {e}")
        return False


def send_test_email():
    """Envia email de teste"""
    print("📧 ENVIO DE EMAIL DE TESTE")
    print("-" * 30)
    
    # Solicitar destinatário
    recipient = input(f"Destinatário (Enter para {settings.EMAIL_HOST_USER}): ").strip()
    if not recipient:
        recipient = settings.EMAIL_HOST_USER
    
    print(f"📮 Enviando para: {recipient}")
    print("⏳ Aguarde...")
    
    try:
        # Dados do email
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        subject = f"✅ Teste Django Bolão - {timestamp}"
        
        message = f"""
Olá! 👋

Este é um email de teste do sistema Django Bolão.

📊 INFORMAÇÕES DO TESTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Data/Hora: {timestamp}
🖥️  Sistema: Bolão Online
🔧 Backend: {settings.EMAIL_BACKEND}
🌐 Host SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
📧 Remetente: {settings.DEFAULT_FROM_EMAIL}
🔐 TLS: {"Ativado" if settings.EMAIL_USE_TLS else "Desativado"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Se você recebeu este email, a configuração Gmail SMTP está funcionando perfeitamente!

🚀 O sistema está pronto para enviar:
   • Notificações de apostas
   • Resultados de jogos
   • Convites para bolões
   • Relatórios de desempenho

📧 Sistema de Email configurado com sucesso!

Atenciosamente,
🏆 Equipe Django Bolão
"""
        
        # Enviar email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        
        if result:
            print("✅ Email enviado com sucesso!")
            print(f"📧 Destinatário: {recipient}")
            print(f"📋 Assunto: {subject}")
            print("🔍 Verifique a caixa de entrada (pode demorar alguns minutos)")
            print()
            print("💡 Dica: Verifique também a pasta de spam/lixo eletrônico")
            return True
        else:
            print("❌ Falha no envio do email (resultado 0)")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        print()
        print("💡 POSSÍVEIS CAUSAS:")
        print("   🔑 Senha de app incorreta ou expirada")
        print("   📱 Verificação em 2 etapas não ativada")
        print("   📧 Email ou configurações inválidas")
        print("   🔥 Firewall bloqueando porta 587")
        print("   🌐 Problemas de conectividade")
        print("   📊 Limites de envio do Gmail atingidos")
        return False


def show_troubleshooting():
    """Exibe dicas de solução de problemas"""
    print("🔧 SOLUÇÃO DE PROBLEMAS")
    print("=" * 40)
    print()
    
    print("❌ Se o teste falhou, verifique:")
    print()
    
    print("🔐 AUTENTICAÇÃO:")
    print("   • Verificação em 2 etapas ativada no Gmail")
    print("   • Senha de app gerada corretamente (16 caracteres)")
    print("   • Email digitado corretamente no .env")
    print()
    
    print("🌐 CONECTIVIDADE:")
    print("   • Conexão com internet funcionando")
    print("   • Firewall não bloqueando porta 587")
    print("   • Proxy corporativo configurado (se aplicável)")
    print()
    
    print("⚙️ CONFIGURAÇÃO:")
    print("   • Arquivo .env no diretório correto")
    print("   • Variáveis de ambiente carregadas pelo Django")
    print("   • Servidor Django reiniciado após alterações")
    print()
    
    print("📊 LIMITES GMAIL:")
    print("   • Máximo 500 emails/dia para contas gratuitas")
    print("   • Máximo 100 destinatários por email")
    print("   • Limite de 2000 emails/dia para G Workspace")


def main():
    """Função principal"""
    print("📧 TESTE DE EMAIL GMAIL - DJANGO BOLÃO")
    print("=" * 50)
    print()
    
    # 1. Verificar configurações
    if not check_email_settings():
        print("❌ Configurações incompletas!")
        print("💡 Execute: python configure_gmail.py")
        return False
    
    print()
    
    # 2. Testar conexão SMTP
    if not test_smtp_connection():
        print()
        show_troubleshooting()
        return False
    
    print()
    
    # 3. Enviar email de teste
    if not send_test_email():
        print()
        show_troubleshooting()
        return False
    
    print()
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 40)
    print("✅ Gmail SMTP configurado e funcionando")
    print("📧 Sistema pronto para produção")
    print("🚀 Emails serão entregues normalmente")
    
    return True


if __name__ == "__main__":
    main()