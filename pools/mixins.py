from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Pool

class PoolOwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que permite acesso apenas ao proprietário do bolão
    """
    def get_pool(self):
        pool_slug = self.kwargs.get('slug')
        return get_object_or_404(Pool, slug=pool_slug)
    
    def test_func(self):
        pool = self.get_pool()
        return self.request.user == pool.owner

class PoolParticipantRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que permite acesso apenas aos participantes do bolão
    """
    def get_pool(self):
        pool_slug = self.kwargs.get('slug')
        return get_object_or_404(Pool, slug=pool_slug)
    
    def test_func(self):
        pool = self.get_pool()
        user = self.request.user
        return user == pool.owner or user in pool.participants.all()

class PoolAvailableForJoinMixin(LoginRequiredMixin):
    """
    Mixin que verifica se um bolão está disponível para ingresso
    """
    def dispatch(self, request, *args, **kwargs):
        self.pool = get_object_or_404(Pool, slug=kwargs.get('slug'))
        if not self.pool.can_join(request.user):
            raise Http404("Este bolão não está disponível para ingresso")
        return super().dispatch(request, *args, **kwargs)