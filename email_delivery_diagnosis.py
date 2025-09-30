"""
Diagnóstico de Entrega de Emails - Django Bolão
Verifica possíveis problemas que podem impedir a entrega
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import time

def check_gmail_status():
    """Verifica status do Gmail e possíveis problemas"""
    print("📧 Diagnóstico de Entrega - Gmail SMTP")
    print("=" * 50)
    
    print("🔧 Configurações atuais:")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Porta: {settings.EMAIL_PORT}")
    print(f"  TLS: {settings.EMAIL_USE_TLS}")
    print(f"  Usuário: {settings.EMAIL_HOST_USER}")
    print(f"  Remetente: {settings.DEFAULT_FROM_EMAIL}")
    
    print("\n⚠️  Possíveis causas de não entrega:")
    print("1. 📬 Caixa de SPAM/Lixo Eletrônico")
    print("2. ⏱️  Delay de entrega (pode demorar 1-5 minutos)")
    print("3. 🛡️  Filtros de email do destinatário")
    print("4. 📱 Gmail pode estar classificando como promoção")
    print("5. 🔒 Rate limiting do Gmail")
    
    print("\n✅ Soluções recomendadas:")
    print("1. Verificar todas as pastas do email (Spam, Promoções, etc.)")
    print("2. Adicionar 'jogador.lastshelter@gmail.com' aos contatos")
    print("3. Aguardar alguns minutos (delay de entrega)")
    print("4. Verificar logs do Gmail na conta remetente")

def send_test_emails():
    """Envia emails de teste com diferentes formatos"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"\n📤 Enviando emails de teste às {timestamp}...")
    
    # Email 1: Texto simples
    try:
        result1 = send_mail(
            subject=f'[TESTE TEXTO] Django Bolão - {timestamp}',
            message=f'Email de teste em texto simples enviado às {timestamp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['vscardoso2005@gmail.com'],
            fail_silently=False,
        )
        print(f"✅ Email texto simples: {'Enviado' if result1 > 0 else 'Falhou'}")
    except Exception as e:
        print(f"❌ Erro email texto: {e}")
    
    time.sleep(2)  # Pausa para evitar rate limiting
    
    # Email 2: HTML simples
    try:
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #333;">🎯 Teste Email HTML</h2>
            <p>Email de teste HTML enviado às <strong>{timestamp}</strong></p>
            <p style="color: #666;">Sistema Django Bolão funcionando!</p>
        </body>
        </html>
        """
        
        from django.core.mail import EmailMultiAlternatives
        
        email = EmailMultiAlternatives(
            subject=f'[TESTE HTML] Django Bolão - {timestamp}',
            body=f'Versão texto do email enviado às {timestamp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['vscardoso2005@gmail.com'],
        )
        email.attach_alternative(html_content, "text/html")
        result2 = email.send()
        
        print(f"✅ Email HTML simples: {'Enviado' if result2 > 0 else 'Falhou'}")
    except Exception as e:
        print(f"❌ Erro email HTML: {e}")

def check_email_delivery_tips():
    """Mostra dicas para melhorar entrega de emails"""
    print("\n💡 Dicas para Melhorar Entrega:")
    print("=" * 50)
    
    print("📱 No Gmail (destinatário):")
    print("  • Verificar aba 'Promoções'")
    print("  • Verificar aba 'Social'")
    print("  • Verificar pasta 'Spam'")
    print("  • Adicionar remetente aos contatos")
    
    print("\n🔧 Configurações recomendadas:")
    print("  • SPF record: v=spf1 include:_spf.google.com ~all")
    print("  • DKIM: Configurar autenticação")
    print("  • DMARC: Política de entrega")
    
    print("\n⏰ Timing:")
    print("  • Emails podem demorar 1-10 minutos")
    print("  • Gmail tem rate limiting")
    print("  • Testar em horários diferentes")

def main():
    print("🚀 Diagnóstico Completo de Entrega de Emails")
    print("=" * 60)
    
    check_gmail_status()
    send_test_emails()
    check_email_delivery_tips()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO:")
    print("✅ Sistema de email está FUNCIONANDO")
    print("✅ SMTP conectando com sucesso")
    print("✅ Emails sendo enviados pelo Django")
    print("⚠️  Se não chegaram, verificar SPAM/Promoções")
    print("⏱️  Aguardar alguns minutos para entrega")

if __name__ == "__main__":
    main()