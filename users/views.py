from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Sum, Count, Q
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .forms import CustomUserCreationForm, UserProfileForm, ProfileEditForm
from .models import CustomUser
from pools.models import Pool, Participation, Bet, Match

# Adicione esta função auxiliar
def cleanup_profile_pictures(user):
    """Verifica e limpa referências de imagens inválidas"""
    try:
        profile = user.profile
        if profile.profile_pic and not profile.profile_pic.storage.exists(profile.profile_pic.name):
            # Referência inválida, limpar campo
            profile.profile_pic = None
            profile.save(update_fields=['profile_pic'])
    except Exception as e:
        print(f"Erro ao verificar imagem do perfil: {e}")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Você já pode fazer login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

class SignupView(CreateView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Faça login automático após o registro, se desejado
        # auth_login(self.request, self.object)
        return response

@login_required
def profile(request):
    # Chame a função no início da view
    cleanup_profile_pictures(request.user)
    
    user = request.user
    
    # Buscar bolões criados pelo usuário - Já corrigido
    owned_pools = Pool.objects.filter(owner=user)
    owned_pools_count = owned_pools.count()
    
    # Buscar bolões que o usuário participa - Já corrigido
    joined_pools = Pool.objects.filter(
        participants=user
    ).exclude(owner=user)  # Excluir os que ele criou
    joined_pools_count = joined_pools.count()
    
    # CORRIGIR: O modelo Bet não tem o campo is_correct
    # Vamos verificar os campos disponíveis e usar points_earned > 0 
    # para identificar apostas corretas
    bets_count = Bet.objects.filter(user=user).count()
    total_points = Bet.objects.filter(user=user).filter(
        points_earned__gt=0  # Apostas com pontos > 0 (corretas)
    ).aggregate(
        Sum('points_earned')
    )['points_earned__sum'] or 0
    
    owned_pools_display = owned_pools[:3]
    joined_pools_display = joined_pools[:3]
    
    recent_activities = []
    
    context = {
        'owned_pools': owned_pools_display,
        'owned_pools_count': owned_pools_count,
        'joined_pools': joined_pools_display,
        'joined_pools_count': joined_pools_count,
        'bets_count': bets_count,
        'total_points': total_points,
        'recent_activities': recent_activities
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirecionar com parâmetro de sucesso para ativar o toast
            return redirect(reverse('users:edit_profile') + '?success=true')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    
    # Bolões dos quais o usuário participa (incluindo os que criou)
    user_pools = Pool.objects.filter(
        Q(owner=user) | Q(participants=user)
    ).distinct().select_related('competition')
    
    # Estatísticas do usuário
    total_pools = user_pools.count()
    owned_pools = Pool.objects.filter(owner=user).count()
    joined_pools = total_pools - owned_pools
    
    # Apostas do usuário
    user_bets = Bet.objects.filter(user=user)
    total_bets = user_bets.count()
    total_points = user_bets.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    
    # Apostas corretas (com pontos > 0)
    correct_bets = user_bets.filter(points_earned__gt=0).count()
    accuracy_rate = (correct_bets / total_bets * 100) if total_bets > 0 else 0
    
    # Próximas partidas (próximos 7 dias)
    today = timezone.now()
    next_week = today + timedelta(days=7)
    
    try:
        upcoming_matches = Match.objects.filter(
            pool__in=user_pools,
            start_time__gte=today,
            start_time__lte=next_week
        ).select_related('pool', 'home_team', 'away_team').order_by('start_time')[:6]
    except:
        # Se o modelo Match não existir ou houver erro, usar lista vazia
        upcoming_matches = []
    
    # Ranking dos pools do usuário (top 3 posições)
    user_rankings = []
    for pool in user_pools[:3]:
        try:
            # Calcular ranking simples baseado nos pontos
            pool_bets = Bet.objects.filter(pool=pool).values('user').annotate(
                total_points=Sum('points_earned')
            ).order_by('-total_points')
            
            user_position = None
            for index, bet_info in enumerate(pool_bets, 1):
                if bet_info['user'] == user.id:
                    user_position = index
                    break
            
            user_rankings.append({
                'pool': pool,
                'position': user_position or '-',
                'total_participants': pool_bets.count()
            })
        except:
            # Em caso de erro, adicionar dados básicos
            user_rankings.append({
                'pool': pool,
                'position': '-',
                'total_participants': pool.participants.count()
            })
    
    # Dados para gráfico de performance (últimos 10 jogos)
    recent_bets = user_bets.order_by('-id')[:10]
    performance_data = []
    cumulative_points = 0
    
    for bet in reversed(recent_bets):
        cumulative_points += bet.points_earned
        performance_data.append({
            'match': f"Jogo {len(performance_data) + 1}",
            'points': bet.points_earned,
            'cumulative': cumulative_points
        })
    
    context = {
        'user': user,
        'total_pools': total_pools,
        'owned_pools': owned_pools,
        'joined_pools': joined_pools,
        'total_bets': total_bets,
        'total_points': total_points,
        'correct_bets': correct_bets,
        'accuracy_rate': round(accuracy_rate, 1),
        'upcoming_matches': upcoming_matches,
        'user_rankings': user_rankings,
        'performance_data': performance_data,
        'active_pools': user_pools.filter(status='active')[:3],
    }
    
    return render(request, 'users/dashboard.html', context)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Mesmo contexto da função dashboard
        user_pools = Pool.objects.filter(
            Q(owner=user) | Q(participants=user)
        ).distinct().select_related('competition')
        
        total_pools = user_pools.count()
        owned_pools = Pool.objects.filter(owner=user).count()
        joined_pools = total_pools - owned_pools
        
        user_bets = Bet.objects.filter(user=user)
        total_bets = user_bets.count()
        total_points = user_bets.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        
        correct_bets = user_bets.filter(points_earned__gt=0).count()
        accuracy_rate = (correct_bets / total_bets * 100) if total_bets > 0 else 0
        
        today = timezone.now()
        next_week = today + timedelta(days=7)
        
        try:
            upcoming_matches = Match.objects.filter(
                pool__in=user_pools,
                start_time__gte=today,
                start_time__lte=next_week
            ).select_related('pool', 'home_team', 'away_team').order_by('start_time')[:6]
        except:
            upcoming_matches = []
        
        user_rankings = []
        for pool in user_pools[:3]:
            try:
                pool_bets = Bet.objects.filter(pool=pool).values('user').annotate(
                    total_points=Sum('points_earned')
                ).order_by('-total_points')
                
                user_position = None
                for index, bet_info in enumerate(pool_bets, 1):
                    if bet_info['user'] == user.id:
                        user_position = index
                        break
                
                user_rankings.append({
                    'pool': pool,
                    'position': user_position or '-',
                    'total_participants': pool_bets.count()
                })
            except:
                user_rankings.append({
                    'pool': pool,
                    'position': '-',
                    'total_participants': pool.participants.count()
                })
        
        recent_bets = user_bets.order_by('-id')[:10]
        performance_data = []
        cumulative_points = 0
        
        for bet in reversed(recent_bets):
            cumulative_points += bet.points_earned
            performance_data.append({
                'match': f"Jogo {len(performance_data) + 1}",
                'points': bet.points_earned,
                'cumulative': cumulative_points
            })
        
        context.update({
            'total_pools': total_pools,
            'owned_pools': owned_pools,
            'joined_pools': joined_pools,
            'total_bets': total_bets,
            'total_points': total_points,
            'correct_bets': correct_bets,
            'accuracy_rate': round(accuracy_rate, 1),
            'upcoming_matches': upcoming_matches,
            'user_rankings': user_rankings,
            'performance_data': performance_data,
            'active_pools': user_pools.filter(status='active')[:3],
        })
        
        return context

def login_view(request):
    # ... código existente ...
    
    if request.method == 'POST':
        # ... código existente de autenticação ...
        
        if user is not None:
            login(request, user)
            
            # Verificar se há um código de convite na sessão
            if 'invitation_code' in request.session:
                code = request.session['invitation_code']
                del request.session['invitation_code']
                
                # Redirecionar para a página de aceitação do convite
                return redirect('pools:accept_invitation', code=code)
                
            # ... resto do código existente ...
