"""
Sistema de emails otimizado para melhor entregabilidade
Versões simplificadas dos templates para evitar filtros de spam
"""

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def send_simple_welcome_email(user):
    """
    Versão simplificada do email de boas-vindas
    Maior chance de entrega sem ser classificado como spam
    """
    try:
        subject = 'Bem-vindo ao Django Bolão!'
        
        # Email em texto simples para melhor entregabilidade
        text_content = f"""
Olá, {user.get_full_name() or user.username}!

Seja bem-vindo ao Django Bolão!

Agora você pode:
- Participar de bolões existentes
- Criar seus próprios bolões
- Convidar amigos para participar
- Fazer apostas e acompanhar resultados

Para começar, acesse: http://localhost:8000/

Boa sorte!

--
Equipe Django Bolão
        """
        
        # HTML simples e limpo
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .content {{ margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #7f8c8d; margin-top: 30px; border-top: 1px solid #ecf0f1; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Bem-vindo ao Django Bolão!</h2>
    </div>
    
    <div class="content">
        <p>Olá, <strong>{user.get_full_name() or user.username}</strong>!</p>
        
        <p>Seja bem-vindo ao Django Bolão!</p>
        
        <p>Agora você pode:</p>
        <ul>
            <li>Participar de bolões existentes</li>
            <li>Criar seus próprios bolões</li>
            <li>Convidar amigos para participar</li>
            <li>Fazer apostas e acompanhar resultados</li>
        </ul>
        
        <p>Para começar, acesse: <a href="http://localhost:8000/">Django Bolão</a></p>
        
        <p>Boa sorte!</p>
    </div>
    
    <div class="footer">
        Equipe Django Bolão<br>
        Este é um email automático.
    </div>
</body>
</html>
        """
        
        # Criar email com versões texto e HTML
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de boas-vindas simples enviado para {user.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas simples para {user.email}: {e}")
        return False


def send_text_only_email(user, subject, message):
    """
    Envia email apenas em texto simples
    Máxima compatibilidade e entregabilidade
    """
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email texto enviado para {user.email}: {subject}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email texto para {user.email}: {e}")
        return False


def send_simple_invitation_email(invitation):
    """
    Versão simplificada do convite para bolão
    """
    try:
        subject = f'Convite para o bolão: {invitation.pool.name}'
        
        inviter = invitation.pool.creator.get_full_name() or invitation.pool.creator.username
        
        message = f"""
Olá!

Você foi convidado por {inviter} para participar do bolão "{invitation.pool.name}".

Detalhes:
- Criado em: {invitation.pool.created_at.strftime('%d/%m/%Y')}
- Organizador: {inviter}

Para aceitar o convite, acesse:
http://localhost:8000/convite/{invitation.token}/

Boa sorte!

--
Django Bolão
        """
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        
        logger.info(f"Convite simples enviado para {invitation.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar convite simples para {invitation.email}: {e}")
        return False


def send_simple_results_email(user, pool, round_data):
    """
    Versão simplificada dos resultados da rodada
    """
    try:
        subject = f'Resultados - {round_data["round_name"]} - {pool.name}'
        
        message = f"""
Olá, {user.get_full_name() or user.username}!

Resultados da {round_data['round_name']} no bolão "{pool.name}":

Sua Performance:
- Pontos nesta rodada: {round_data['round_points']}
- Total acumulado: {round_data['total_points']}
- Posição atual: {round_data['current_position']}º lugar
- Acertos: {round_data['correct_predictions']}/{round_data['total_predictions']}

Ver mais detalhes: http://localhost:8000/bolao/{pool.id}/

Boa sorte na próxima rodada!

--
Django Bolão
        """
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Resultados simples enviados para {user.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar resultados simples para {user.email}: {e}")
        return False


def test_email_deliverability():
    """
    Testa diferentes tipos de email para verificar entregabilidade
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado para teste")
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    print(f"🧪 Testando entregabilidade às {timestamp}")
    print("=" * 50)
    
    # Teste 1: Email texto puro
    print("1. Testando email texto puro...")
    result1 = send_text_only_email(
        user,
        f"[TESTE TEXTO] {timestamp}",
        f"Email de teste em texto puro enviado às {timestamp}"
    )
    print(f"   {'✅ Enviado' if result1 else '❌ Falhou'}")
    
    # Teste 2: Email HTML simples
    print("\n2. Testando email HTML simples...")
    result2 = send_simple_welcome_email(user)
    print(f"   {'✅ Enviado' if result2 else '❌ Falhou'}")
    
    # Teste 3: Email HTML complexo (original)
    print("\n3. Testando email HTML complexo...")
    try:
        from .email import send_welcome_email
        result3 = send_welcome_email(user)
        print(f"   {'✅ Enviado' if result3 else '❌ Falhou'}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos testes:")
    print(f"Texto puro: {'✅' if result1 else '❌'}")
    print(f"HTML simples: {'✅' if result2 else '❌'}")
    print("\n💡 Recomendação:")
    print("Use emails mais simples para melhor entregabilidade")


if __name__ == "__main__":
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
    django.setup()
    
    test_email_deliverability()