from django.shortcuts import render
from pools.models import Pool

def home(request):
    context = {}
    
    # Se o usuário estiver autenticado, calcular suas estatísticas
    if request.user.is_authenticated:
        try:
            # Bolões onde o usuário é o dono - usando campo status em vez de is_active
            user_pools = Pool.objects.filter(
                owner=request.user,
                status='active'  # Substituído is_active por status='active'
            ).distinct()
            
            # Bolões onde o usuário participa
            participating_pools = Pool.objects.filter(
                participation__user=request.user,
                status='active'  # Substituído is_active por status='active'
            ).distinct()
            
            # Combinando ambos os conjuntos
            all_user_pools = (user_pools | participating_pools).distinct()
            
            context['active_pools_count'] = all_user_pools.count()
            
            # Contar total de participantes
            total_participants = 0
            for pool in all_user_pools:
                # +1 para o dono
                total_participants += pool.participation_set.count() + 1
            
            context['total_participants'] = total_participants
            
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")
            # Valores padrão para não quebrar o template
            context['active_pools_count'] = 0
            context['total_participants'] = 0
        
        # Estatísticas para administradores
        if request.user.is_staff:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            context['admin_stats'] = {
                'total_pools': Pool.objects.count(),
                'total_users': User.objects.filter(is_active=True).count(),
            }
    
    # Estatísticas gerais do site (visible para todos)
    total_pools = Pool.objects.filter(status='active').count()  # Substituído is_active por status
    context['site_stats'] = {
        'total_pools': total_pools
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')
