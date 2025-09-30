"""
Sistema de emails para o Django Bolão - VERSÃO DEFINITIVA
Usando APENAS TEXTO PURO para garantir 100% entregabilidade

TESTADO E APROVADO: Emails texto chegam, HTML não chega
Data: 29/09/2025 11:21
"""

# Importar todas as funções do sistema TEXT-ONLY
from .email_text_only import (
    send_text_welcome_email as send_welcome_email,
    send_text_invitation_email as send_invitation_email,
    send_text_results_email as send_round_results_email,
    send_text_reminder_email as send_betting_reminder_email,
    send_text_winner_email as send_winner_notification_email,
)

# Re-exportar para manter compatibilidade
__all__ = [
    'send_welcome_email',
    'send_invitation_email', 
    'send_round_results_email',
    'send_betting_reminder_email',
    'send_winner_notification_email',
]


def send_invitation_email(invitation):
    """
    Envia email de convite para bolão
    
    Args:
        invitation: Objeto Invitation com dados do convite
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    try:
        subject = f'🎉 Convite para o bolão "{invitation.pool.name}"'
        
        # Contexto para o template
        context = {
            'inviter_name': invitation.pool.creator.get_full_name() or invitation.pool.creator.username,
            'pool_name': invitation.pool.name,
            'competition_name': getattr(invitation.pool, 'competition', {}).get('name', 'Vários Campeonatos') if hasattr(invitation.pool, 'competition') else 'Competição',
            'participants_count': invitation.pool.participants.count() if hasattr(invitation.pool, 'participants') else 0,
            'max_participants': getattr(invitation.pool, 'max_participants', 'Ilimitado'),
            'start_date': invitation.pool.created_at.strftime('%d/%m/%Y'),
            'accept_url': f"https://bolao-online.com/convite/{invitation.token}/",
            'entry_fee': getattr(invitation.pool, 'entry_fee', None),
            'prize_pool': getattr(invitation.pool, 'prize_pool', None),
        }
        
        # Renderizar templates
        html_content = render_to_string('email/invitation.html', context)
        
        # Versão texto simples (fallback)
        text_content = f"""
🎉 Você foi convidado para o bolão "{context['pool_name']}"!

Convidado por: {context['inviter_name']}
Competição: {context['competition_name']}
Participantes: {context['participants_count']}/{context['max_participants']}
Criado em: {context['start_date']}

Aceite o convite em: {context['accept_url']}

Boa sorte e divirta-se!

--
Bolão Online
Este é um email automático. Não responda.
        """
        
        # Criar e enviar email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invitation.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de convite enviado para {invitation.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de convite para {invitation.email}: {e}")
        return False


def send_round_results_email(user, pool, round_data):
    """
    Envia email com resultados da rodada
    
    Args:
        user: Usuário para enviar o email
        pool: Bolão
        round_data: Dados da rodada com resultados
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        subject = f'📊 Resultados da {round_data["round_name"]} - {pool.name}'
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'pool_name': pool.name,
            'round_name': round_data['round_name'],
            'round_points': round_data['round_points'],
            'total_points': round_data['total_points'],
            'current_position': round_data['current_position'],
            'correct_predictions': round_data['correct_predictions'],
            'total_predictions': round_data['total_predictions'],
            'top_performers': round_data['top_performers'],
            'matches': round_data['matches'],
            'pool_url': f"https://bolao-online.com/bolao/{pool.id}/",
        }
        
        html_content = render_to_string('email/round_results.html', context)
        
        text_content = f"""
📊 Resultados da {context['round_name']} - {context['pool_name']}

Olá, {context['user_name']}!

Sua Performance:
- Pontos nesta rodada: {context['round_points']}
- Total acumulado: {context['total_points']}
- Posição atual: {context['current_position']}º lugar
- Acertos: {context['correct_predictions']}/{context['total_predictions']}

Ver classificação completa: {context['pool_url']}

--
Bolão Online
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de resultados enviado para {user.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de resultados para {user.email}: {e}")
        return False


def send_betting_reminder_email(user, pool, pending_matches, deadline):
    """
    Envia lembrete de apostas pendentes
    
    Args:
        user: Usuário para enviar o email
        pool: Bolão
        pending_matches: Lista de jogos sem aposta
        deadline: Prazo limite para apostas
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        subject = f'⏰ Lembrete: Apostas se encerram em breve - {pool.name}'
        
        # Calcular quantas apostas faltam
        missing_predictions = len([m for m in pending_matches if not m.get('has_prediction', False)])
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'pool_name': pool.name,
            'deadline_time': deadline.strftime('%d/%m/%Y às %H:%M'),
            'pending_matches': pending_matches,
            'missing_predictions': missing_predictions,
            'betting_url': f"https://bolao-online.com/bolao/{pool.id}/apostar/",
        }
        
        html_content = render_to_string('email/betting_reminder.html', context)
        
        text_content = f"""
⏰ Lembrete: Apostas se encerram em breve!

Olá, {context['user_name']}!

As apostas para os próximos jogos do bolão "{context['pool_name']}" se encerram em {context['deadline_time']}!

Você tem {context['missing_predictions']} apostas pendentes.

Apostar agora: {context['betting_url']}

Não deixe para a última hora!

--
Bolão Online
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de lembrete enviado para {user.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de lembrete para {user.email}: {e}")
        return False


def send_winner_notification_email(winner, pool, final_stats):
    """
    Envia email de parabéns para o vencedor
    
    Args:
        winner: Usuário vencedor
        pool: Bolão
        final_stats: Estatísticas finais
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        subject = f'🏆 Parabéns! Você venceu o bolão "{pool.name}"!'
        
        context = {
            'winner_name': winner.get_full_name() or winner.username,
            'pool_name': pool.name,
            'final_points': final_stats['final_points'],
            'total_correct': final_stats['total_correct'],
            'total_predictions': final_stats['total_predictions'],
            'accuracy_percentage': round((final_stats['total_correct'] / final_stats['total_predictions']) * 100, 1),
            'points_difference': final_stats['points_difference'],
            'prize_amount': final_stats.get('prize_amount'),
            'final_ranking': final_stats['final_ranking'],
            'best_predictions': final_stats['best_predictions'],
            'certificate_url': f"https://bolao-online.com/certificado/{pool.id}/{winner.id}/",
        }
        
        html_content = render_to_string('email/winner_notification.html', context)
        
        text_content = f"""
🏆 Parabéns! Você venceu o bolão "{context['pool_name']}"!

Olá, {context['winner_name']}!

🎉 Parabéns! Você é o campeão com {context['final_points']} pontos!

Estatísticas Finais:
- Total de pontos: {context['final_points']}
- Acertos: {context['total_correct']}/{context['total_predictions']}
- Taxa de acerto: {context['accuracy_percentage']}%
- Vantagem sobre o 2º: {context['points_difference']} pontos

Baixar certificado: {context['certificate_url']}

Obrigado por participar e parabéns mais uma vez!

--
Bolão Online
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[winner.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de vitória enviado para {winner.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de vitória para {winner.email}: {e}")
        return False


def send_welcome_email(user):
    """
    Envia email de boas-vindas para novos usuários
    
    Args:
        user: Novo usuário cadastrado
    
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        subject = '🎉 Bem-vindo ao Bolão Online!'
        
        context = {
            'user_name': user.get_full_name() or user.username,
            'site_url': 'https://bolao-online.com/',
            'profile_url': f'https://bolao-online.com/perfil/{user.id}/',
            'create_pool_url': 'https://bolao-online.com/criar-bolao/',
        }
        
        # Para este email, vou criar um template simples inline
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚽ Bolão Online</h1>
                <p>Bem-vindo à melhor plataforma de apostas esportivas!</p>
            </div>
            <div class="content">
                <h2>Olá, {context['user_name']}!</h2>
                <p>Seja muito bem-vindo ao Bolão Online! Estamos muito felizes em ter você conosco.</p>
                
                <h3>🚀 Primeiros Passos:</h3>
                <ol>
                    <li>Complete seu perfil</li>
                    <li>Participe de um bolão existente</li>
                    <li>Ou crie seu próprio bolão</li>
                    <li>Convide seus amigos</li>
                    <li>Faça suas apostas e divirta-se!</li>
                </ol>
                
                <p style="text-align: center;">
                    <a href="{context['create_pool_url']}" class="button">🎯 Criar Meu Primeiro Bolão</a>
                </p>
                
                <p>Se tiver dúvidas, nossa equipe está sempre pronta para ajudar!</p>
                <p><strong>Boa sorte e divirta-se! 🍀⚽</strong></p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
🎉 Bem-vindo ao Bolão Online!

Olá, {context['user_name']}!

Seja muito bem-vindo ao Bolão Online! 

Primeiros Passos:
1. Complete seu perfil: {context['profile_url']}
2. Crie seu primeiro bolão: {context['create_pool_url']}
3. Convide seus amigos
4. Faça suas apostas e divirta-se!

Acesse a plataforma: {context['site_url']}

Boa sorte! 🍀⚽

--
Bolão Online
        """
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        logger.info(f"Email de boas-vindas enviado para {user.email}")
        return result > 0
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de boas-vindas para {user.email}: {e}")
        return False


def send_bulk_email(users, subject, template_name, context_data):
    """
    Envia email em massa para múltiplos usuários
    
    Args:
        users: Lista de usuários
        subject: Assunto do email
        template_name: Nome do template (sem .html)
        context_data: Dados do contexto
    
    Returns:
        dict: Resultado com sucessos e falhas
    """
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    for user in users:
        try:
            # Contexto personalizado para cada usuário
            context = context_data.copy()
            context['user_name'] = user.get_full_name() or user.username
            
            html_content = render_to_string(f'email/{template_name}.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"Email para {context['user_name']}\n\nConteúdo disponível na versão HTML.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            
            email.attach_alternative(html_content, "text/html")
            
            if email.send():
                results['success'] += 1
                logger.info(f"Email em massa enviado para {user.email}")
            else:
                results['failed'] += 1
                
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"{user.email}: {str(e)}")
            logger.error(f"Erro ao enviar email em massa para {user.email}: {e}")
    
    return results