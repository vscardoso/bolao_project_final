from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileForm, ProfileEditForm
from .models import CustomUser
from pools.models import Pool, Participation, Bet

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
    
    # Obtenha bolões dos quais o usuário participa
    participations = Participation.objects.filter(user=user).select_related('pool')
    pools = [p.pool for p in participations]
    
    # Obtenha também bolões que o usuário criou
    owned_pools = Pool.objects.filter(owner=user)
    
    context = {
        'user': user,
        'participating_pools': pools,
        'owned_pools': owned_pools,
        'total_pools': len(pools) + len(owned_pools)
    }
    return render(request, 'users/dashboard.html', context)

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
