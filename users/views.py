from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm
from .models import CustomUser
from pools.models import Pool, Participation

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

@login_required
def profile(request):
    user = request.user
    return render(request, 'users/profile.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
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
