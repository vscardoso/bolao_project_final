from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect
from datetime import timedelta

from .models import Pool, Participation, Sport, Competition, Bet, Match
from .forms import PoolForm, PoolJoinForm, BetForm
from .mixins import PoolOwnerRequiredMixin, PoolParticipantRequiredMixin, PoolUserAccessMixin

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

class BetCreateView(LoginRequiredMixin, PoolUserAccessMixin, CreateView):
    model = Bet
    form_class = BetForm
    template_name = 'pools/bet_form.html'
    
    def setup(self, request, *args, **kwargs):
        """Configurar a view com o pool_id correto baseado na slug"""
        self.pool_object = get_object_or_404(Pool, slug=kwargs.get('slug'))
        kwargs['pool_id'] = self.pool_object.id
        super().setup(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        match = self.get_match()
        kwargs['match'] = match
        kwargs['pool'] = self.get_pool()
        
        # Verificar se já existe uma aposta e passar como instance para o form
        existing_bet = self.get_existing_bet()
        if existing_bet:
            kwargs['instance'] = existing_bet
        
        return kwargs
    
    def get_match(self):
        match_id = self.kwargs.get('match_id')
        return get_object_or_404(Match, pk=match_id)
    
    def get_pool(self):
        return self.pool_object
    
    def get_existing_bet(self):
        """Verifica se já existe uma aposta para este usuário/partida/bolão"""
        return Bet.objects.filter(
            user=self.request.user,
            pool=self.get_pool(),
            match=self.get_match()
        ).first()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.pool = self.get_pool()
        form.instance.match = self.get_match()
        
        # Verificar se já existe uma aposta
        existing_bet = self.get_existing_bet()
        
        if existing_bet:
            # Atualizar os campos em vez de criar uma nova aposta
            existing_bet.home_score_bet = form.cleaned_data['home_score_bet']
            existing_bet.away_score_bet = form.cleaned_data['away_score_bet']
            existing_bet.save()
            messages.success(self.request, "Sua aposta foi atualizada com sucesso!")
            return HttpResponseRedirect(self.get_success_url())
        
        # Caso contrário, criar uma nova aposta
        messages.success(self.request, "Sua aposta foi registrada com sucesso!")
        return super().form_valid(form)
    
    def get_success_url(self):
        pool = self.get_pool()
        return reverse('pools:detail', kwargs={'slug': pool.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.get_pool()
        context['match'] = self.get_match()
        context['existing_bet'] = self.get_existing_bet()
        return context

class BetListView(LoginRequiredMixin, PoolUserAccessMixin, ListView):
    model = Bet
    template_name = 'pools/bet_list.html'
    context_object_name = 'bets'
    
    def setup(self, request, *args, **kwargs):
        """Configurar a view com o pool_id correto baseado na slug"""
        self.pool_object = get_object_or_404(Pool, slug=kwargs.get('slug'))
        kwargs['pool_id'] = self.pool_object.id
        super().setup(request, *args, **kwargs)
    
    def get_queryset(self):
        return Bet.objects.filter(pool=self.get_pool(), user=self.request.user)
    
    def get_pool(self):
        return self.pool_object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pool'] = self.get_pool()
        
        # Incluir partidas disponíveis para aposta
        context['available_matches'] = Match.objects.filter(
            competition=self.get_pool().competition,
            finished=False,
            start_time__gt=timezone.now()
        ).order_by('start_time')
        
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

@login_required
def bet_match(request, pool_id, match_id):
    """View para criar ou atualizar uma aposta em uma partida"""
    
    # Buscar o pool e a partida
    pool = get_object_or_404(Pool, id=pool_id)
    match = get_object_or_404(Match, id=match_id)
    
    # Verificar se o usuário é participante do pool
    if request.user not in pool.participants.all() and request.user != pool.owner:
        messages.error(request, "Você não é participante deste bolão.")
        return redirect('pools:detail', pool_id=pool_id)
    
    # Verificar se a partida já começou
    if match.start_time <= timezone.now():
        messages.error(request, "O prazo para apostas nesta partida já encerrou.")
        return redirect('pools:detail', pool_id=pool_id)
    
    # Verificar se existe uma aposta prévia
    existing_bet = Bet.objects.filter(
        user=request.user,
        pool=pool,
        match=match
    ).first()
    
    # Verificar se o prazo está próximo (menos de 24h)
    is_deadline_close = match.start_time - timezone.now() < timedelta(hours=24)
    
    if request.method == 'POST':
        form = BetForm(request.POST, instance=existing_bet)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.pool = pool
            bet.match = match
            bet.save()
            
            messages.success(request, "Sua aposta foi registrada com sucesso!")
            return redirect('pools:detail', pool_id=pool_id)
    else:
        form = BetForm(instance=existing_bet)
    
    context = {
        'pool': pool,
        'match': match,
        'form': form,
        'existing_bet': existing_bet,
        'is_deadline_close': is_deadline_close,
    }
    
    return render(request, 'pools/bet_form.html', context)

def calculate_bet_points(bet):
    """Calcula os pontos ganhos por uma aposta após o resultado da partida"""
    
    match = bet.match
    
    # Verificar se a partida foi finalizada e tem resultado
    if not match.finished or match.home_score is None or match.away_score is None:
        return 0
    
    # Resultados reais
    real_home_score = match.home_score
    real_away_score = match.away_score
    
    # Apostas do usuário
    bet_home_score = bet.home_score_bet
    bet_away_score = bet.away_score_bet
    
    # Verificar resultado real (vitória casa, empate ou vitória visitante)
    if real_home_score > real_away_score:
        real_result = 'home'
    elif real_home_score < real_away_score:
        real_result = 'away'
    else:
        real_result = 'draw'
    
    # Verificar resultado apostado
    if bet_home_score > bet_away_score:
        bet_result = 'home'
    elif bet_home_score < bet_away_score:
        bet_result = 'away'
    else:
        bet_result = 'draw'
    
    # Acertou placar exato (10 pontos)
    if bet_home_score == real_home_score and bet_away_score == real_away_score:
        return 10
    
    # Acertou o vencedor e o saldo de gols (5 pontos)
    if bet_result == real_result and (bet_home_score - bet_away_score) == (real_home_score - real_away_score):
        return 5
    
    # Acertou apenas o vencedor (3 pontos)
    if bet_result == real_result:
        return 3
    
    # Não acertou nada (0 pontos)
    return 0

def pool_ranking(request, slug):
    """Exibe a classificação dos participantes de um bolão"""
    pool = get_object_or_404(Pool, slug=slug)
    
    # Verificar se o usuário pode ver o bolão
    if pool.visibility == 'private' and request.user != pool.owner and not pool.participants.filter(id=request.user.id).exists():
        messages.error(request, "Você não tem acesso a este bolão.")
        return redirect('pools:list')
    
    # Obter todos os participantes com suas pontuações
    participants_data = []
    
    for participant in pool.participants.all():
        # Obter todas as apostas do participante neste bolão
        bets = Bet.objects.filter(user=participant, pool=pool)
        total_points = bets.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        bets_count = bets.count()
        correct_bets = bets.filter(points_earned__gt=0).count()
        
        # Calcular aproveitamento
        accuracy = 0
        if bets_count > 0:
            accuracy = (correct_bets / bets_count) * 100
        
        participants_data.append({
            'user': participant,
            'points': total_points,
            'bets_count': bets_count,
            'correct_bets': correct_bets,
            'accuracy': accuracy,
        })
    
    # Ordenar por pontos (maior para menor)
    participants_data.sort(key=lambda x: x['points'], reverse=True)
    
    return render(request, 'pools/ranking.html', {'pool': pool, 'participants': participants_data})
