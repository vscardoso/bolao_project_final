from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import Pool

class PoolOwnerRequiredMixin:
    """Mixin que verifica se o usuário é o dono do bolão"""
    
    def dispatch(self, request, *args, **kwargs):
        pool = get_object_or_404(Pool, pk=kwargs.get('pk'))
        if pool.owner != request.user:
            messages.error(request, 'Apenas o criador do bolão pode realizar esta ação.')
            return redirect('pools:detail', pk=pool.id)
        return super().dispatch(request, *args, **kwargs)

class PoolParticipantRequiredMixin:
    """Mixin que verifica se o usuário é participante do bolão"""
    
    def dispatch(self, request, *args, **kwargs):
        pool = get_object_or_404(Pool, pk=kwargs.get('pk'))
        if not pool.participants.filter(id=request.user.id).exists():
            messages.error(request, 'Você precisa ser participante deste bolão para realizar esta ação.')
            return redirect('pools:detail', pk=pool.id)
        return super().dispatch(request, *args, **kwargs)

class PoolUserAccessMixin:
    """Mixin que verifica se o usuário tem acesso ao bolão (dono ou participante)"""
    
    def test_func(self, request, pool_id):
        """Testa se o usuário tem acesso ao bolão"""
        pool = get_object_or_404(Pool, pk=pool_id)
        
        # Verifica se o usuário é o dono ou um participante
        if pool.owner == request.user or pool.participants.filter(id=request.user.id).exists():
            return True
            
        # Se não tiver acesso, adiciona mensagem de erro
        messages.error(request, 'Você não tem permissão para acessar este bolão.')
        return False
    
    def dispatch(self, request, *args, **kwargs):
        pool_id = kwargs.get('pool_id')
        
        if not pool_id and 'slug' in kwargs:
            # Se não temos pool_id mas temos slug, busque o pool pelo slug
            pool = get_object_or_404(Pool, slug=kwargs.get('slug'))
            pool_id = pool.id
            
        if not self.test_func(request, pool_id):
            return redirect('pools:list')
            
        return super().dispatch(request, *args, **kwargs)