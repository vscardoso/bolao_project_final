"""
View de teste para demonstrar o formulário de apostas aprimorado
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Match, Pool, Bet, Participation
from .forms import BetForm

@login_required
def test_bet_form(request, match_id=None, pool_id=None):
    """
    View de teste para o formulário de apostas aprimorado
    """
    # Se não foi fornecido match_id, pegar uma partida de exemplo
    if match_id:
        match = get_object_or_404(Match, id=match_id)
    else:
        # Pegar uma partida futura para teste
        match = Match.objects.filter(
            start_time__gte=timezone.now(),
            finished=False
        ).first()
        
        if not match:
            # Se não há partidas futuras, criar uma de exemplo
            from .models import Team, Competition
            home_team, _ = Team.objects.get_or_create(
                name="Brasil", 
                defaults={'country': 'BR'}
            )
            away_team, _ = Team.objects.get_or_create(
                name="Argentina", 
                defaults={'country': 'AR'}
            )
            competition, _ = Competition.objects.get_or_create(
                name="Copa do Mundo 2026",
                defaults={'is_active': True}
            )
            
            match = Match.objects.create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                start_time=timezone.now() + timezone.timedelta(hours=24),
                round_name="Final"
            )
    
    # Pool opcional para teste
    pool = None
    if pool_id:
        pool = get_object_or_404(Pool, id=pool_id)
    
    # Verificar se o usuário já tem uma aposta nesta partida
    existing_bet = None
    if pool:
        try:
            existing_bet = Bet.objects.get(
                user=request.user,
                match=match,
                participation__pool=pool
            )
        except Bet.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = BetForm(
            request.POST, 
            instance=existing_bet,
            match=match,
            pool=pool,
            user=request.user
        )
        
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.match = match
            
            # Se há um pool, associar à participação
            if pool:
                try:
                    participation = Participation.objects.get(
                        user=request.user,
                        pool=pool
                    )
                    bet.participation = participation
                except Participation.DoesNotExist:
                    messages.error(request, 'Você precisa participar do bolão primeiro.')
                    return redirect('pools:pool_detail', pool_id=pool.id)
            
            bet.save()
            
            if existing_bet:
                messages.success(request, '✅ Aposta atualizada com sucesso!')
            else:
                messages.success(request, '🎉 Aposta realizada com sucesso!')
            
            # Redirecionar para o dashboard ou detalhe do pool
            if pool:
                return redirect('pools:pool_detail', pool_id=pool.id)
            else:
                return redirect('pools:dashboard')
        else:
            messages.error(request, '❌ Erro ao processar a aposta. Verifique os dados.')
    else:
        form = BetForm(
            instance=existing_bet,
            match=match,
            pool=pool,
            user=request.user
        )
    
    context = {
        'form': form,
        'match': match,
        'pool': pool,
        'existing_bet': existing_bet,
        'now': timezone.now(),
    }
    
    return render(request, 'pools/bet_form_example.html', context)