# -*- coding: utf-8 -*-
"""
SISTEMA DE NOTIFICAÇÕES E SIGNALS
Automatiza notificações por email e atualiza estatísticas
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from .models import Match, Invitation, Participation, Bet, Pool
from users.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Match)
def notify_result_updated(sender, instance, **kwargs):
    """Notifica usuários quando resultado de partida é atualizado"""
    if instance.finished and instance.home_score is not None:
        # Buscar apostas dessa partida
        bets = instance.bet_set.select_related('user', 'pool')
        
        for bet in bets:
            try:
                subject = f'🎯 Resultado: {instance.home_team} vs {instance.away_team}'
                
                # Determinar se acertou ou errou
                points = bet.points_earned
                if points >= 10:
                    result_emoji = "🎉"
                    result_text = "ACERTOU EM CHEIO!"
                elif points >= 5:
                    result_emoji = "👏"
                    result_text = "Boa! Acertou quase tudo!"
                elif points >= 3:
                    result_emoji = "👍"
                    result_text = "Acertou o resultado!"
                else:
                    result_emoji = "😅"
                    result_text = "Não foi dessa vez..."
                
                context = {
                    'user': bet.user,
                    'match': instance,
                    'bet': bet,
                    'result': f'{instance.home_score} x {instance.away_score}',
                    'prediction': f'{bet.home_score_bet} x {bet.away_score_bet}',
                    'points': points,
                    'result_emoji': result_emoji,
                    'result_text': result_text,
                    'pool': bet.pool,
                }
                
                # Renderizar template HTML
                html_message = render_to_string('email/result_notification.html', context)
                
                # Enviar email
                send_mail(
                    subject,
                    f"""
{result_emoji} {result_text}

Partida: {instance.home_team} {instance.home_score} x {instance.away_score} {instance.away_team}
Sua aposta: {bet.home_score_bet} x {bet.away_score_bet}
Pontos ganhos: {points}

Bolão: {bet.pool.name}
                    """,
                    settings.DEFAULT_FROM_EMAIL,
                    [bet.user.email],
                    fail_silently=True,
                    html_message=html_message,
                )
                
                logger.info(f"Notificação de resultado enviada para {bet.user.username}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar notificação de resultado: {e}")


@receiver(post_save, sender=Participation)
def notify_pool_creator(sender, instance, created, **kwargs):
    """Notifica criador quando alguém entra no bolão"""
    if created and instance.pool.owner != instance.user:
        try:
            subject = f'🎉 {instance.user.username} entrou no seu bolão!'
            
            context = {
                'pool_owner': instance.pool.owner,
                'new_participant': instance.user,
                'pool': instance.pool,
                'total_participants': instance.pool.participation_set.count(),
                'max_participants': instance.pool.max_participants,
            }
            
            # Renderizar template HTML
            html_message = render_to_string('email/new_participant.html', context)
            
            message = f"""
Olá {instance.pool.owner.username},

{instance.user.username} acaba de entrar no bolão "{instance.pool.name}".

Total de participantes: {instance.pool.participation_set.count()}/{instance.pool.max_participants if instance.pool.max_participants > 0 else '∞'}

Boa sorte para todos! 🍀
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.pool.owner.email],
                fail_silently=True,
                html_message=html_message,
            )
            
            logger.info(f"Notificação de novo participante enviada para {instance.pool.owner.username}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de novo participante: {e}")


@receiver(post_save, sender=Bet)
def notify_bet_deadline_approaching(sender, instance, created, **kwargs):
    """Notifica sobre deadline de apostas se estiver próximo"""
    if created:
        try:
            # Verificar se o deadline está próximo (menos de 2 horas)
            time_until_match = instance.match.start_time - timezone.now()
            
            if time_until_match.total_seconds() < 7200:  # 2 horas
                subject = f'⏰ Última chance de apostar!'
                
                context = {
                    'user': instance.user,
                    'match': instance.match,
                    'pool': instance.pool,
                    'time_remaining': time_until_match,
                }
                
                # Buscar outras partidas do mesmo pool próximas sem apostas
                upcoming_matches = Match.objects.filter(
                    pool=instance.pool,
                    start_time__gt=timezone.now(),
                    start_time__lt=timezone.now() + timezone.timedelta(hours=24),
                    finished=False
                ).exclude(
                    bet__user=instance.user
                )[:3]
                
                if upcoming_matches.exists():
                    context['upcoming_matches'] = upcoming_matches
                    
                    html_message = render_to_string('email/deadline_reminder.html', context)
                    
                    send_mail(
                        subject,
                        f"Oi {instance.user.username}! Você tem partidas próximas para apostar no bolão {instance.pool.name}.",
                        settings.DEFAULT_FROM_EMAIL,
                        [instance.user.email],
                        fail_silently=True,
                        html_message=html_message,
                    )
                    
                    logger.info(f"Lembrete de deadline enviado para {instance.user.username}")
                    
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete de deadline: {e}")


@receiver(post_save, sender=Match)
def update_bet_points_on_result(sender, instance, **kwargs):
    """Atualiza pontuação das apostas quando partida finaliza"""
    if instance.finished and instance.home_score is not None and instance.away_score is not None:
        try:
            # Buscar todas as apostas dessa partida
            bets = Bet.objects.filter(match=instance)
            
            for bet in bets:
                # Calcular pontos
                old_points = bet.points_earned
                new_points = bet.calculate_points()
                
                if old_points != new_points:
                    bet.points_earned = new_points
                    bet.save(update_fields=['points_earned'])
                    
                    # Atualizar estatísticas da participação
                    participation = Participation.objects.get(user=bet.user, pool=bet.pool)
                    total_points = Bet.objects.filter(
                        user=bet.user, 
                        pool=bet.pool, 
                        match__finished=True
                    ).aggregate(total=Sum('points_earned'))['total'] or 0
                    
                    participation.points = total_points
                    participation.save(update_fields=['points'])
                    
            logger.info(f"Pontuação atualizada para {bets.count()} apostas da partida {instance}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar pontuação das apostas: {e}")


@receiver(post_save, sender=Invitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """Envia email de convite quando convite é criado"""
    if created:
        try:
            subject = f'🎲 Convite para o bolão "{instance.pool.name}"'
            
            context = {
                'invitation': instance,
                'pool': instance.pool,
                'sender': instance.sender,
                'accept_url': f"{settings.SITE_URL}/pools/convite/{instance.code}/aceitar/",
                'decline_url': f"{settings.SITE_URL}/pools/convite/{instance.code}/recusar/",
            }
            
            html_message = render_to_string('email/invitation.html', context)
            
            message = f"""
Olá!

{instance.sender.username} te convidou para participar do bolão "{instance.pool.name}".

{instance.message}

Para aceitar: {context['accept_url']}
Para recusar: {context['decline_url']}

Boa sorte! 🍀
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.recipient_email],
                fail_silently=True,
                html_message=html_message,
            )
            
            logger.info(f"Convite enviado para {instance.recipient_email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar convite por email: {e}")


# Signal para criar estatísticas automáticas
@receiver(post_save, sender=Bet)
def update_pool_statistics(sender, instance, created, **kwargs):
    """Atualiza estatísticas do pool quando aposta é criada"""
    if created:
        try:
            pool = instance.pool
            
            # Atualizar total de apostas do pool
            total_bets = Bet.objects.filter(pool=pool).count()
            
            # Atualizar estatísticas se o modelo Pool tiver esses campos
            if hasattr(pool, 'total_bets'):
                pool.total_bets = total_bets
                pool.save(update_fields=['total_bets'])
            
            # Atualizar total de apostas da partida
            match = instance.match
            if hasattr(match, 'total_bets'):
                match.total_bets = match.bet_set.count()
                match.save(update_fields=['total_bets'])
                
            logger.info(f"Estatísticas atualizadas para pool {pool.name}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar estatísticas: {e}")


# Signal para notificar ranking semanal
def notify_weekly_ranking():
    """Função para ser chamada por um cron job semanal"""
    from django.db.models import Sum
    from datetime import timedelta
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Para cada pool ativo
    active_pools = Pool.objects.filter(status='open')
    
    for pool in active_pools:
        try:
            # Calcular ranking semanal
            weekly_ranking = Bet.objects.filter(
                pool=pool,
                created_at__gte=one_week_ago,
                match__finished=True
            ).values('user').annotate(
                weekly_points=Sum('points_earned')
            ).order_by('-weekly_points')[:3]
            
            if weekly_ranking:
                # Enviar para todos os participantes
                participants = pool.participation_set.select_related('user')
                
                for participation in participants:
                    context = {
                        'user': participation.user,
                        'pool': pool,
                        'weekly_ranking': weekly_ranking,
                    }
                    
                    html_message = render_to_string('email/weekly_ranking.html', context)
                    
                    send_mail(
                        f'📊 Ranking semanal - {pool.name}',
                        f"Confira o ranking da semana no bolão {pool.name}!",
                        settings.DEFAULT_FROM_EMAIL,
                        [participation.user.email],
                        fail_silently=True,
                        html_message=html_message,
                    )
                    
                logger.info(f"Ranking semanal enviado para pool {pool.name}")
                
        except Exception as e:
            logger.error(f"Erro ao enviar ranking semanal: {e}")