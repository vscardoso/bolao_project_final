from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum, F, Case, When, Value
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.utils.text import slugify
import logging
import csv
from datetime import datetime, timedelta

from .models import Pool, Participation, Sport, Competition, Bet, Match
from .forms import PoolForm, PoolJoinForm, BetForm
from .mixins import PoolOwnerRequiredMixin, PoolParticipantRequiredMixin, PoolUserAccessMixin
from pools.models import Invitation
from pools.forms import InvitationForm
from django.db import IntegrityError

logger = logging.getLogger(__name__)

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
        
        context['selected_sport'] = self.request.GET.get('sport', '')
        context['search'] = self.request.GET.get('search', '')
        
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

class PoolUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pool
    form_class = PoolForm
    template_name = 'pools/pool_update.html'
    
    def test_func(self):
        pool = self.get_object()
        return self.request.user == pool.owner
    
    def get_success_url(self):
        return reverse('pools:detail', kwargs={'slug': self.object.slug})

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

class InvitationListView(LoginRequiredMixin, View):
    
    def get(self, request, slug=None):
        # Se não receber um slug, mostrar todos os convites enviados pelo usuário
        if not slug:
            # Buscar todos os convites que o usuário enviou
            invitations = Invitation.objects.filter(
                sender=request.user
            ).order_by('-created_at')
            
            return render(request, 'pools/all_invitations_list.html', {
                'invitations': invitations
            })
            
        # Para um bolão específico
        pool = get_object_or_404(Pool, slug=slug)
        
        # Verificar se o usuário é o dono ou administrador do bolão
        if not pool.is_owner_or_admin(request.user):
            messages.error(request, "Apenas o dono ou administradores podem ver os convites.")
            return redirect('pools:detail', slug=pool.slug)
        
        invitations = Invitation.objects.filter(pool=pool).order_by('-created_at')
        return render(request, 'pools/invitations_list.html', {
            'invitations': invitations,
            'pool': pool
        })

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
    """Exibe a lista de bolões criados pelo usuário"""
    template_name = 'pools/my_pools.html'
    context_object_name = 'pools'
    
    def get_queryset(self):
        # Obter todos os bolões onde o usuário é o dono
        queryset = Pool.objects.filter(owner=self.request.user).order_by('-created_at')
        
        # Adicionar filtros se necessário
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
            
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
            
        sport = self.request.GET.get('sport', '')
        if sport:
            queryset = queryset.filter(competition__sport_id=sport)
        
        # Debug para ver quantos bolões estão sendo encontrados
        print(f"Encontrados {queryset.count()} bolões criados pelo usuário {self.request.user.username}")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'created'
        context['active_tab'] = 'my_created'
        
        # Adicionar contagem de bolões que o usuário participa
        if self.request.user.is_authenticated:
            context['joined_pools_count'] = Participation.objects.filter(
                user=self.request.user
            ).count()
        else:
            context['joined_pools_count'] = 0
        
        return context

class MyJoinedPoolsView(LoginRequiredMixin, ListView):
    """Exibe a lista de bolões que o usuário participa"""
    template_name = 'pools/my_pools.html'
    context_object_name = 'pools'
    
    def get_queryset(self):
        # Obter IDs dos bolões em que o usuário participa
        participation_pool_ids = Participation.objects.filter(
            user=self.request.user
        ).values_list('pool_id', flat=True)
        
        # Retornar queryset excluindo bolões que o próprio usuário criou
        return Pool.objects.filter(
            id__in=participation_pool_ids
        ).exclude(
            owner=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = 'joined'
        context['active_tab'] = 'my_joined'
        
        # Adicionar contagem de bolões que o usuário participa
        if self.request.user.is_authenticated:
            context['joined_pools_count'] = Participation.objects.filter(
                user=self.request.user
            ).count()
        else:
            context['joined_pools_count'] = 0
            
        return context

@login_required
def bet_match(request, slug, match_id):  # <-- Alterado de pool_id para slug
    """View para criar ou atualizar uma aposta em uma partida"""
    
    # Buscar o pool e a partida usando slug
    pool = get_object_or_404(Pool, slug=slug)  # <-- Alterado para buscar por slug
    match = get_object_or_404(Match, id=match_id)
    
    # Verificar se o usuário é participante do pool
    if request.user not in pool.participants.all() and request.user != pool.owner:
        messages.error(request, "Você não é participante deste bolão.")
        return redirect('pools:detail', slug=pool.slug)  # <-- Corrigido
    
    # Verificar se a partida já começou
    if match.start_time <= timezone.now():
        messages.error(request, "O prazo para apostas nesta partida já encerrou.")
        return redirect('pools:detail', slug=pool.slug)  # <-- Corrigido
    
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
            return redirect('pools:detail', slug=pool.slug)
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
    
    # Acertou placar exato (10 pontos)
    if bet_home_score == real_home_score and bet_away_score == real_away_score:
        return 10
    
    # Para empates, regra especial
    if real_home_score == real_away_score and bet_home_score == bet_away_score:
        # Se ambos são empates mas com placares diferentes, é 3 pontos
        if real_home_score != bet_home_score:
            return 3
    
    # Acertou o vencedor e o saldo de gols (5 pontos)
    real_diff = real_home_score - real_away_score
    bet_diff = bet_home_score - bet_away_score
    
    if (real_diff == bet_diff) and (
        (real_home_score > real_away_score and bet_home_score > bet_away_score) or
        (real_home_score < real_away_score and bet_home_score < bet_away_score)
    ):
        return 5
    
    # Acertou apenas o vencedor (3 pontos)
    if (real_home_score > real_away_score and bet_home_score > bet_away_score) or \
       (real_home_score < real_away_score and bet_home_score < bet_away_score) or \
       (real_home_score == real_away_score and bet_home_score == bet_away_score):
        return 3
    
    # Não acertou nada (0 pontos)
    return 0

def pool_ranking(request, slug):
    """Exibe o ranking geral de participantes do bolão"""
    pool = get_object_or_404(Pool, slug=slug)
    
    # Verifica se o usuário tem acesso
    if pool.visibility == 'private' and request.user not in pool.participants.all() and request.user != pool.owner:
        messages.error(request, "Você não tem acesso a este bolão.")
        return redirect('pools:discover')
    
    # Busca todos os participantes com pontuação
    participants = Participation.objects.filter(pool=pool)\
        .select_related('user')\
        .order_by('-points')
    
    context = {
        'pool': pool,
        'participants': participants,
        'is_owner': request.user == pool.owner,
        'is_participant': Participation.objects.filter(pool=pool, user=request.user).exists() if request.user.is_authenticated else False,
        'active_tab': 'ranking',
        'now': timezone.now(),
    }
    return render(request, 'pools/ranking.html', context)

@login_required
def weekly_ranking(request, slug):
    """Exibe o ranking com base nas apostas da última semana"""
    pool = get_object_or_404(Pool, slug=slug)
    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Busca apostas da semana
    weekly_bets = Bet.objects.filter(
        pool=pool,
        created_at__gte=one_week_ago
    ).values('user').annotate(
        weekly_points=Sum('points_earned')
    ).order_by('-weekly_points')
    
    # Busca informações completas dos usuários
    users_dict = {}
    for bet in weekly_bets:
        if bet['user'] not in users_dict:
            user = CustomUser.objects.get(id=bet['user'])
            users_dict[bet['user']] = {
                'user': user,
                'weekly_points': bet['weekly_points'],
                'profile_pic': user.profile.profile_pic if hasattr(user, 'profile') else None
            }
    
    # Converte para lista e adiciona posição no ranking
    weekly_ranking = list(users_dict.values())
    for i, item in enumerate(weekly_ranking):
        item['position'] = i + 1
    
    context = {
        'pool': pool,
        'weekly_ranking': weekly_ranking,
        'active_tab': 'ranking',
        'ranking_period': 'weekly'
    }
    
    return render(request, 'pools/ranking_weekly.html', context)

@login_required
def export_ranking(request, slug):
    """Exporta o ranking para arquivo CSV"""
    pool = get_object_or_404(Pool, slug=slug)
    
    # Verifica se o usuário tem acesso
    if request.user != pool.owner and request.user not in pool.participants.all():
        messages.error(request, "Você não tem acesso para exportar este ranking.")
        return redirect('pools:discover')
        
    participants = Participation.objects.filter(pool=pool).select_related('user').order_by('-points')
    
    # Cria o arquivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{pool.name}_ranking.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Posição', 'Usuário', 'Pontos', 'Apostas', 'Aproveitamento (%)'])
    
    rank = 1
    previous_points = None
    for participant in participants:
        if previous_points is not None and participant.points != previous_points:
            rank += 1
        writer.writerow([
            rank,
            participant.user.username,
            participant.points,
            participant.total_bets,
            participant.accuracy
        ])
        previous_points = participant.points
    
    return response

class InvitationCreateView(LoginRequiredMixin, View):
    """View para enviar convites para um bolão"""
    
    def get(self, request, slug):
        pool = get_object_or_404(Pool, slug=slug)
        
        # Verificar se o usuário é o dono ou administrador do bolão
        if not pool.is_owner_or_admin(request.user):
            messages.error(request, "Apenas o dono ou administradores podem enviar convites.")
            return redirect('pools:detail', slug=pool.slug)
        
        form = InvitationForm()
        return render(request, 'pools/send_invitation.html', {
            'form': form,
            'pool': pool
        })
    
    def post(self, request, slug):
        pool = get_object_or_404(Pool, slug=slug)
        
        # Verificar se o usuário é o dono ou administrador do bolão
        if not pool.is_owner_or_admin(request.user):
            messages.error(request, "Apenas o dono ou administradores podem enviar convites.")
            return redirect('pools:detail', slug=pool.slug)
        
        form = InvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.pool = pool
            invitation.sender = request.user
            
            # Verificar se o usuário já está no bolão
            recipient_email = form.cleaned_data['recipient_email']
            user_exists = User.objects.filter(email=recipient_email).exists()
            
            if user_exists:
                user = User.objects.get(email=recipient_email)
                if Participation.objects.filter(user=user, pool=pool).exists():
                    messages.warning(request, "Este usuário já está participando do bolão.")
                    return redirect('pools:detail', slug=pool.slug)
            
            # Verificar se já existe um convite pendente
            existing_invitation = Invitation.objects.filter(
                pool=pool,
                recipient_email=recipient_email,
                status='pending'
            ).exists()
            
            if existing_invitation:
                messages.warning(request, "Já existe um convite pendente para este e-mail.")
                return redirect('pools:invitations', slug=pool.slug)
            
            try:
                invitation.save()
                messages.success(request, "Convite enviado com sucesso!")
                
                # Enviar e-mail aqui (implementação futura)
                # send_invitation_email(invitation)
                
                return redirect('pools:invitations', slug=pool.slug)
            except IntegrityError:
                messages.error(request, "Erro ao enviar convite. Tente novamente.")
        
        return render(request, 'pools/send_invitation.html', {
            'form': form,
            'pool': pool
        })

def accept_invitation(request, code):
    """View para aceitar um convite"""
    invitation = get_object_or_404(Invitation, code=code, status='pending')
    
    if not request.user.is_authenticated:
        # Salvar o código na sessão e redirecionar para o login
        request.session['invitation_code'] = code
        messages.info(request, "Faça login para aceitar o convite para o bolão.")
        return redirect('login')
    
    # Verificar se o e-mail do convite corresponde ao usuário logado
    if invitation.recipient_email != request.user.email:
        messages.error(request, "Este convite é destinado a outro endereço de e-mail.")
        return redirect('home')
    
    # Verificar se o usuário já está no bolão
    if Participation.objects.filter(user=request.user, pool=invitation.pool).exists():
        invitation.status = 'accepted'
        invitation.save()
        messages.info(request, "Você já está participando deste bolão.")
        return redirect('pools:detail', slug=invitation.pool.slug)
    
    # Criar participação e atualizar status do convite
    Participation.objects.create(
        user=request.user,
        pool=invitation.pool,
        payment_status='pending' if invitation.pool.entry_fee > 0 else 'paid'
    )
    
    invitation.status = 'accepted'
    invitation.save()
    
    messages.success(request, f"Você entrou no bolão {invitation.pool.name}!")
    return redirect('pools:detail', slug=invitation.pool.slug)

def decline_invitation(request, code):
    """View para recusar um convite"""
    invitation = get_object_or_404(Invitation, code=code, status='pending')
    
    if not request.user.is_authenticated:
        # Salvar o código na sessão e redirecionar para o login
        request.session['invitation_code'] = code
        messages.info(request, "Faça login para responder ao convite para o bolão.")
        return redirect('login')
    
    # Verificar se o e-mail do convite corresponde ao usuário logado
    if invitation.recipient_email != request.user.email:
        messages.error(request, "Este convite é destinado a outro endereço de e-mail.")
        return redirect('home')
    
    # Atualizar status do convite
    invitation.status = 'declined'
    invitation.save()
    
    messages.info(request, f"Você recusou o convite para o bolão {invitation.pool.name}.")
    return redirect('home')

def criar_bolao_brasileirao(request):
    # Obter o campeonato brasileiro mais recente
    try:
        brasileirao = Campeonato.objects.filter(nome__icontains='Brasileiro').latest('temporada')
    except Campeonato.DoesNotExist:
        messages.error(request, "Campeonato Brasileiro não encontrado no sistema.")
        return redirect('pools:create')
    
    if request.method == 'POST':
        form = PoolForm(request.POST, request.FILES)
        if form.is_valid():
            bolao = form.save(commit=False)
            bolao.owner = request.user
            bolao.campeonato = brasileirao
            bolao.importar_jogos_automaticamente = True
            bolao.save()
            form.save_m2m()  # Salva relações ManyToMany
            
            # Importar jogos automaticamente
            num_jogos = bolao.importar_jogos_do_campeonato()
            
            messages.success(request, f"Bolão do Brasileirão criado com sucesso! {num_jogos} jogos importados.")
            return redirect('pools:detail', slug=bolao.slug)
    else:
        # Formulário pré-preenchido para o Brasileirão
        form = PoolForm(initial={
            'name': f'Brasileirão {brasileirao.temporada}',
            'description': f'Bolão do Campeonato Brasileiro {brasileirao.temporada}',
            'entry_fee': 50.00,  # Valor sugerido
            'sport': Sport.objects.get(name='Futebol')
        })
    
    return render(request, 'pools/criar_bolao_brasileirao.html', {
        'form': form,
        'campeonato': brasileirao
    })

def create_tournament_pool(request, tournament_slug):
    """Cria um bolão para um torneio específico"""
    
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    
    if request.method == 'POST':
        form = PoolForm(request.POST, request.FILES)
        if form.is_valid():
            pool = form.save(commit=False)
            pool.owner = request.user
            pool.tournament = tournament
            pool.import_matches_automatically = form.cleaned_data.get('import_matches_automatically', True)
            
            # Configurar sistema de pontuação
            pool.exact_score_points = form.cleaned_data.get('exact_score_points', 10)
            pool.correct_difference_points = form.cleaned_data.get('correct_difference_points', 5)
            pool.correct_winner_points = form.cleaned_data.get('correct_winner_points', 3)
            pool.wrong_points = form.cleaned_data.get('wrong_points', 0)
            
            pool.save()
            form.save_m2m()
            
            # Importar jogos se configurado
            matches_imported = 0
            if pool.import_matches_automatically:
                matches_imported = pool.import_tournament_matches()
            
            messages.success(
                request, 
                f"Bolão {pool.name} criado com sucesso! {matches_imported} jogos importados."
            )
            return redirect('pools:detail', slug=pool.slug)
    else:
        # Formulário pré-preenchido
        form = PoolForm(initial={
            'name': f"{tournament.name} {tournament.season}",
            'description': f"Bolão do {tournament.name} {tournament.season}",
            'entry_fee': 50.00,  # Valor sugerido
            'sport': tournament.sport,
            'import_matches_automatically': True,
            'exact_score_points': 10,
            'correct_difference_points': 5,
            'correct_winner_points': 3,
            'wrong_points': 0,
        })
    
    return render(request, 'pools/create_tournament_pool.html', {
        'form': form,
        'tournament': tournament
    })
