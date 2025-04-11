from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import HttpResponseRedirect

from .models import Pool, Participation, Sport, Competition, Bet, Match
from .forms import PoolForm, PoolJoinForm, BetForm
from .mixins import PoolOwnerRequiredMixin, PoolParticipantRequiredMixin

class PoolListView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/pool_list.html'
    context_object_name = 'pools'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Bolões que o usuário criou
        owned_pools = Pool.objects.filter(owner=user)
        context['owned_pools'] = owned_pools
        context['owned_pools_count'] = owned_pools.count()
        
        # Bolões que o usuário participa (mas não criou)
        participating_pools = Pool.objects.filter(
            participation__user=user,
            participation__payment_status__in=['paid', 'completed']
        ).exclude(owner=user).distinct()
        context['participating_pools'] = participating_pools
        context['joined_pools_count'] = participating_pools.count()  # Adicionando esta variável
        
        # Bolões públicos que o usuário pode participar
        context['available_pools'] = Pool.objects.filter(
            visibility='public', 
            status='open'
        ).exclude(
            Q(owner=user) | Q(participation__user=user)
        ).order_by('-created_at')[:5]
        
        return context

class PoolCreateView(LoginRequiredMixin, CreateView):
    """View para criar um bolão"""
    model = Pool
    form_class = PoolForm
    template_name = 'pools/create_pool.html'
    success_url = reverse_lazy('pools:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        # Salvar o bolão primeiro
        response = super().form_valid(form)
        
        # Adicionar o criador como participante automaticamente
        from pools.models import Participation  # Importação local para evitar referência circular
        Participation.objects.create(
            user=self.request.user,
            pool=self.object,
            payment_status='paid'  # Dono não precisa pagar
        )
        
        messages.success(self.request, "Bolão criado com sucesso!")
        return response

class PoolDetailView(DetailView):
    model = Pool
    template_name = 'pools/pool_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pool = self.get_object()
        
        # Informações básicas do bolão
        context['is_owner'] = pool.owner == self.request.user
        
        # Buscar corretamente os participantes através da relação Participation
        context['participants'] = pool.participation_set.all().select_related('user').order_by('-points')
        context['participants_count'] = context['participants'].count()
        
        # Verificar se o usuário atual é um participante
        if self.request.user.is_authenticated:
            context['is_participant'] = Participation.objects.filter(
                user=self.request.user, 
                pool=pool
            ).exists()
        
        # Partidas da competição
        context['upcoming_matches'] = Match.objects.filter(
            competition=pool.competition,
            finished=False,
            start_time__gt=timezone.now()
        ).order_by('start_time')
        
        context['now'] = timezone.now()
        
        return context

class PoolUpdateView(PoolOwnerRequiredMixin, UpdateView):
    """View para editar um bolão"""
    model = Pool
    form_class = PoolForm
    template_name = 'pools/pool_form.html'
    
    def get_success_url(self):
        return reverse('pools:detail', kwargs={'slug': self.object.slug})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Bolão atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Bolão'
        context['submit_text'] = 'Salvar Alterações'
        return context

class PoolDeleteView(PoolOwnerRequiredMixin, DeleteView):
    """View para excluir um bolão"""
    model = Pool
    template_name = 'pools/pool_confirm_delete.html'
    success_url = reverse_lazy('pools:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Bolão excluído com sucesso!")
        return super().delete(request, *args, **kwargs)

class PoolJoinView(LoginRequiredMixin, View):
    template_name = 'pools/pool_join.html'
    
    def get_pool(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Pool, slug=slug)
    
    def get(self, request, *args, **kwargs):
        pool = self.get_pool()
        
        # Verifica se o usuário já participa
        if Participation.objects.filter(user=request.user, pool=pool).exists():
            messages.info(request, 'Você já participa deste bolão.')
            return redirect('pools:detail', slug=pool.slug)
            
        form = PoolJoinForm(initial={'pool': pool})
        return render(request, self.template_name, {'pool': pool, 'form': form})
    
    def post(self, request, *args, **kwargs):
        pool = self.get_pool()
        form = PoolJoinForm(request.POST)
        
        # Verificar se o formulário é válido antes de acessar cleaned_data
        if form.is_valid():
            # Agora podemos acessar cleaned_data com segurança
            payment_method = form.cleaned_data.get('payment_method')
            
            # Criar participação
            participation = Participation(
                user=request.user,
                pool=pool,
                payment_method=payment_method,
                payment_status='pending'
            )
            participation.save()
            
            messages.success(request, f'Você se juntou ao bolão {pool.name}!')
            return redirect('pools:detail', slug=pool.slug)
        else:
            # Formulário não é válido, renderizar novamente com erros
            return render(request, self.template_name, {'pool': pool, 'form': form})

class PoolDiscoverView(LoginRequiredMixin, ListView):
    """View para descobrir bolões disponíveis"""
    model = Pool
    template_name = 'pools/pool_discover.html'
    context_object_name = 'pools'
    paginate_by = 12
    
    def get_queryset(self):
        user = self.request.user
        # Filtrar bolões públicos que o usuário não participa
        queryset = Pool.objects.filter(
            visibility='public',
            status='open'
        ).exclude(
            Q(owner=user) | Q(participants=user)
        ).select_related('owner', 'competition')
        
        # Adicionar filtros adicionais se houver
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(competition__name__icontains=search)
            )
        
        # Filtro por esporte
        sport_id = self.request.GET.get('sport')
        if sport_id and sport_id.isdigit():
            queryset = queryset.filter(competition__sport_id=sport_id)
        
        # Ordenação
        order_by = self.request.GET.get('order_by', '-created_at')
        if order_by in ['name', '-name', 'entry_fee', '-entry_fee', 'created_at', '-created_at']:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sports'] = Sport.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['selected_sport'] = self.request.GET.get('sport', '')
        context['order_by'] = self.request.GET.get('order_by', '-created_at')
        return context

class InvitationListView(LoginRequiredMixin, ListView):
    """View para listar convites de bolões"""
    template_name = 'pools/invitation_list.html'
    context_object_name = 'invitations'
    
    def get_queryset(self):
        # Aqui você precisaria de um modelo Invitation ou similar
        # Como não temos este modelo implementado ainda, retornamos uma lista vazia
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aqui você pode adicionar convites enviados pelo usuário
        # context['sent_invitations'] = Invitation.objects.filter(sender=self.request.user)
        return context

class BetCreateView(LoginRequiredMixin, CreateView):
    model = Bet
    form_class = BetForm
    template_name = 'pools/bet_form.html'
    
    def get_success_url(self):
        return reverse('pools:detail', kwargs={'slug': self.kwargs['slug']})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.pool = get_object_or_404(Pool, slug=self.kwargs['slug'])
        self.match = get_object_or_404(Match, pk=self.kwargs['match_id'])
        kwargs['match'] = self.match
        kwargs['pool'] = self.pool
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        context['match'] = self.match
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.match = self.match
        form.instance.pool = self.pool
        
        # Verificar se o usuário participa do bolão
        if not Participation.objects.filter(user=self.request.user, pool=self.pool).exists():
            messages.error(self.request, "Você precisa participar deste bolão para fazer uma aposta.")
            return self.form_invalid(form)
        
        # Verificar se já existe uma aposta deste usuário para esta partida
        existing_bet = Bet.objects.filter(user=self.request.user, match=self.match, pool=self.pool).first()
        if existing_bet:
            # Se existir, atualizar ao invés de criar
            existing_bet.home_score_bet = form.cleaned_data['home_score_bet']
            existing_bet.away_score_bet = form.cleaned_data['away_score_bet']
            existing_bet.save()
            messages.success(self.request, "Sua aposta foi atualizada!")
            return HttpResponseRedirect(self.get_success_url())
        
        messages.success(self.request, "Aposta registrada com sucesso!")
        return super().form_valid(form)

class BetListView(LoginRequiredMixin, ListView):
    model = Bet
    template_name = 'pools/bet_list.html'
    context_object_name = 'bets'
    
    def get_queryset(self):
        self.pool = get_object_or_404(Pool, slug=self.kwargs['slug'])
        return Bet.objects.filter(user=self.request.user, pool=self.pool)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.pool
        return context

class MyCreatedPoolsView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/my_created_pools.html'
    context_object_name = 'pools'
    
    def get_queryset(self):
        return Pool.objects.filter(owner=self.request.user)

class MyJoinedPoolsView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/my_joined_pools.html'
    context_object_name = 'pools'
    
    def get_queryset(self):
        return Pool.objects.filter(
            participation__user=self.request.user,
            participation__payment_status__in=['paid', 'completed']
        ).exclude(owner=self.request.user)

class DiscoverPoolsView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/discover_pools.html'
    context_object_name = 'pools'
    
    def get_queryset(self):
        return Pool.objects.filter(
            visibility='public', 
            status='open'
        ).exclude(
            Q(owner=self.request.user) | Q(participation__user=self.request.user)
        )
