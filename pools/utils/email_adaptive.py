"""
Sistema Inteligente de Emails - Django Bolão
Detecta problemas de entregabilidade e adapta automaticamente
"""

from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.utils import timezone
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailDeliveryManager:
    """
    Gerenciador inteligente de entrega de emails
    Adapta formato baseado na entregabilidade
    """
    
    def __init__(self):
        self.delivery_stats = {
            'html_complex': 0,
            'html_simple': 0,
            'text_only': 0,
            'failed': 0
        }
    
    def send_adaptive_email(self, user, email_type, **kwargs):
        """
        Envia email adaptando formato para melhor entregabilidade
        """
        # Primeiro tenta HTML simples
        if self._send_simple_html_email(user, email_type, **kwargs):
            self.delivery_stats['html_simple'] += 1
            return True
        
        # Se falhar, tenta apenas texto
        if self._send_text_only_email(user, email_type, **kwargs):
            self.delivery_stats['text_only'] += 1
            return True
        
        self.delivery_stats['failed'] += 1
        return False
    
    def _send_simple_html_email(self, user, email_type, **kwargs):
        """Envia email HTML simplificado"""
        try:
            subject, text_content, html_content = self._get_email_content(user, email_type, **kwargs)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            
            email.attach_alternative(html_content, "text/html")
            result = email.send()
            
            if result > 0:
                logger.info(f"Email HTML simples enviado para {user.email}: {email_type}")
                return True
            
        except Exception as e:
            logger.warning(f"Falha HTML simples para {user.email}: {e}")
        
        return False
    
    def _send_text_only_email(self, user, email_type, **kwargs):
        """Envia email apenas texto"""
        try:
            subject, text_content, _ = self._get_email_content(user, email_type, **kwargs)
            
            result = send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            if result > 0:
                logger.info(f"Email texto enviado para {user.email}: {email_type}")
                return True
            
        except Exception as e:
            logger.error(f"Falha texto para {user.email}: {e}")
        
        return False
    
    def _get_email_content(self, user, email_type, **kwargs):
        """Gera conteúdo do email baseado no tipo"""
        
        user_name = user.get_full_name() or user.username
        
        if email_type == 'welcome':
            return self._get_welcome_content(user_name)
        
        elif email_type == 'invitation':
            return self._get_invitation_content(user_name, **kwargs)
        
        elif email_type == 'results':
            return self._get_results_content(user_name, **kwargs)
        
        elif email_type == 'reminder':
            return self._get_reminder_content(user_name, **kwargs)
        
        else:
            return self._get_generic_content(user_name, **kwargs)
    
    def _get_welcome_content(self, user_name):
        """Conteúdo do email de boas-vindas"""
        subject = "Bem-vindo ao Django Bolão!"
        
        text_content = f"""
Olá, {user_name}!

Seja bem-vindo ao Django Bolão!

O que você pode fazer:
• Participar de bolões existentes
• Criar seus próprios bolões
• Convidar amigos
• Fazer apostas e acompanhar resultados

Acesse: http://localhost:8000/

Boa sorte!

--
Equipe Django Bolão
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            max-width: 600px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        .header {{ 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px; 
            margin-bottom: 20px;
        }}
        .content {{ margin: 20px 0; }}
        .footer {{ 
            font-size: 12px; 
            color: #7f8c8d; 
            margin-top: 30px; 
            border-top: 1px solid #ecf0f1; 
            padding-top: 10px; 
        }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin: 8px 0; }}
        li:before {{ content: "• "; color: #3498db; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Bem-vindo ao Django Bolão!</h2>
    </div>
    
    <div class="content">
        <p>Olá, <strong>{user_name}</strong>!</p>
        
        <p>Seja bem-vindo ao Django Bolão!</p>
        
        <p>O que você pode fazer:</p>
        <ul>
            <li>Participar de bolões existentes</li>
            <li>Criar seus próprios bolões</li>
            <li>Convidar amigos</li>
            <li>Fazer apostas e acompanhar resultados</li>
        </ul>
        
        <p><a href="http://localhost:8000/" style="color: #3498db;">Acesse o Django Bolão</a></p>
        
        <p>Boa sorte!</p>
    </div>
    
    <div class="footer">
        Equipe Django Bolão
    </div>
</body>
</html>
        """
        
        return subject, text_content.strip(), html_content
    
    def _get_invitation_content(self, user_name, invitation=None, **kwargs):
        """Conteúdo do email de convite"""
        pool_name = invitation.pool.name if invitation else kwargs.get('pool_name', 'Bolão')
        inviter = invitation.pool.creator.get_full_name() or invitation.pool.creator.username if invitation else kwargs.get('inviter', 'Organizador')
        
        subject = f"Convite para o bolão: {pool_name}"
        
        text_content = f"""
Olá!

Você foi convidado por {inviter} para participar do bolão "{pool_name}".

Para aceitar o convite, acesse:
http://localhost:8000/

Boa sorte!

--
Django Bolão
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; margin-bottom: 20px; }}
        .content {{ margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #7f8c8d; margin-top: 30px; border-top: 1px solid #ecf0f1; padding-top: 10px; }}
        .button {{ background: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Convite para Bolão!</h2>
    </div>
    
    <div class="content">
        <p>Olá!</p>
        
        <p>Você foi convidado por <strong>{inviter}</strong> para participar do bolão "<strong>{pool_name}</strong>".</p>
        
        <p><a href="http://localhost:8000/" class="button">Aceitar Convite</a></p>
        
        <p>Boa sorte!</p>
    </div>
    
    <div class="footer">
        Django Bolão
    </div>
</body>
</html>
        """
        
        return subject, text_content.strip(), html_content
    
    def _get_results_content(self, user_name, **kwargs):
        """Conteúdo do email de resultados"""
        pool_name = kwargs.get('pool_name', 'Bolão')
        round_name = kwargs.get('round_name', 'Rodada')
        points = kwargs.get('points', 0)
        position = kwargs.get('position', '-')
        
        subject = f"Resultados - {round_name} - {pool_name}"
        
        text_content = f"""
Olá, {user_name}!

Resultados da {round_name} no bolão "{pool_name}":

Sua Performance:
• Pontos: {points}
• Posição: {position}º lugar

Ver mais: http://localhost:8000/

--
Django Bolão
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 10px; margin-bottom: 20px; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Resultados - {round_name}</h2>
    </div>
    
    <div class="stats">
        <p><strong>Sua Performance:</strong></p>
        <p>• Pontos: {points}</p>
        <p>• Posição: {position}º lugar</p>
    </div>
    
    <p><a href="http://localhost:8000/" style="color: #27ae60;">Ver classificação completa</a></p>
</body>
</html>
        """
        
        return subject, text_content.strip(), html_content
    
    def _get_reminder_content(self, user_name, **kwargs):
        """Conteúdo do email de lembrete"""
        pool_name = kwargs.get('pool_name', 'Bolão')
        deadline = kwargs.get('deadline', 'em breve')
        
        subject = f"Lembrete: Apostas se encerram {deadline}"
        
        text_content = f"""
Olá, {user_name}!

As apostas do bolão "{pool_name}" se encerram {deadline}!

Não esqueça de fazer suas apostas!

Apostar: http://localhost:8000/

--
Django Bolão
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ color: #2c3e50; border-bottom: 2px solid #f39c12; padding-bottom: 10px; margin-bottom: 20px; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>⏰ Lembrete de Apostas</h2>
    </div>
    
    <div class="alert">
        <p><strong>As apostas do bolão "{pool_name}" se encerram {deadline}!</strong></p>
        <p>Não esqueça de fazer suas apostas!</p>
    </div>
    
    <p><a href="http://localhost:8000/" style="color: #f39c12;">Apostar agora</a></p>
</body>
</html>
        """
        
        return subject, text_content.strip(), html_content
    
    def _get_generic_content(self, user_name, **kwargs):
        """Conteúdo genérico"""
        subject = kwargs.get('subject', 'Django Bolão')
        message = kwargs.get('message', 'Mensagem do Django Bolão')
        
        text_content = f"""
Olá, {user_name}!

{message}

--
Django Bolão
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
    </style>
</head>
<body>
    <h2>{subject}</h2>
    <p>Olá, <strong>{user_name}</strong>!</p>
    <p>{message}</p>
    <hr>
    <p><small>Django Bolão</small></p>
</body>
</html>
        """
        
        return subject, text_content.strip(), html_content
    
    def get_stats(self):
        """Retorna estatísticas de entrega"""
        total = sum(self.delivery_stats.values())
        if total == 0:
            return "Nenhum email enviado ainda"
        
        return f"""
Estatísticas de Entrega:
• HTML Simples: {self.delivery_stats['html_simple']} ({self.delivery_stats['html_simple']/total*100:.1f}%)
• Apenas Texto: {self.delivery_stats['text_only']} ({self.delivery_stats['text_only']/total*100:.1f}%)
• Falhas: {self.delivery_stats['failed']} ({self.delivery_stats['failed']/total*100:.1f}%)
• Total: {total} emails
        """


# Instância global do gerenciador
email_manager = EmailDeliveryManager()

# Funções de conveniência
def send_welcome_email(user):
    """Envia email de boas-vindas adaptativo"""
    return email_manager.send_adaptive_email(user, 'welcome')

def send_invitation_email(invitation):
    """Envia convite adaptativo"""
    return email_manager.send_adaptive_email(invitation, 'invitation', invitation=invitation)

def send_results_email(user, pool_name, round_name, points, position):
    """Envia resultados adaptativos"""
    return email_manager.send_adaptive_email(
        user, 'results',
        pool_name=pool_name,
        round_name=round_name,
        points=points,
        position=position
    )

def send_reminder_email(user, pool_name, deadline):
    """Envia lembrete adaptativo"""
    return email_manager.send_adaptive_email(
        user, 'reminder',
        pool_name=pool_name,
        deadline=deadline
    )

def get_delivery_stats():
    """Obtém estatísticas de entrega"""
    return email_manager.get_stats()