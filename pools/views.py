from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View, TemplateView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum, F, Case, When, Value, Avg
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import logging
import csv
from datetime import timedelta

from .models import Pool, Participation, Bet, Match, Sport
from .forms import PoolForm, PoolJoinForm, BetForm, PoolWizardStepOneForm, PoolWizardStepTwoForm, PoolWizardStepThreeForm
from .mixins import PoolOwnerRequiredMixin, PoolUserAccessMixin
from pools.models import Invitation
from pools.forms import InvitationForm
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Obter o modelo de usuário configurado
User = get_user_model()

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pools/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Bolões ativos
        active_pools = Participation.objects.filter(
            user=user,
            pool__status='open'
        ).select_related('pool')
        
        # Próximas partidas para apostar (próximas 48h)
        upcoming_deadline = timezone.now() + timedelta(hours=48)
        upcoming_matches = Match.objects.filter(
            pool__in=[p.pool for p in active_pools],
            start_time__lte=upcoming_deadline,
            start_time__gte=timezone.now(),
            finished=False
        ).exclude(
            bet__user=user  # Excluir partidas já apostadas
        ).order_by('start_time')[:5]
        
        # Estatísticas gerais
        total_bets = Bet.objects.filter(user=user).count()
        finished_bets = Bet.objects.filter(user=user, match__finished=True)
        
        if finished_bets.exists():
            avg_points = finished_bets.aggregate(Avg('points_earned'))['points_earned__avg']
            total_points = finished_bets.aggregate(Sum('points_earned'))['points_earned__sum']
            
            # Taxa de acerto (apostas com pontos > 0)
            correct_bets = finished_bets.filter(points_earned__gt=0).count()
            hit_rate = (correct_bets / finished_bets.count() * 100) if finished_bets.count() > 0 else 0
        else:
            avg_points = 0
            total_points = 0
            hit_rate = 0
        
        # Rankings nos bolões
        pool_rankings = []
        for participation in active_pools:
            pool = participation.pool
            # Calcular ranking do usuário neste bolão
            user_points = Bet.objects.filter(
                user=user,
                pool=pool,
                match__finished=True
            ).aggregate(Sum('points_earned'))['points_earned__sum'] or 0
            
            # Total de participantes
            participants = pool.participation_set.count()
            
            # Posição do usuário
            better_users = Bet.objects.filter(
                pool=pool,
                match__finished=True
            ).values('user').annotate(
                total=Sum('points_earned')
            ).filter(total__gt=user_points).count()
            
            position = better_users + 1
            
            pool_rankings.append({
                'pool': pool,
                'position': position,
                'total_participants': participants,
                'points': user_points
            })
        
        context.update({
            'active_pools': active_pools,
            'upcoming_matches': upcoming_matches,
            'total_bets': total_bets,
            'avg_points': round(avg_points, 1) if avg_points else 0,
            'total_points': total_points or 0,
            'hit_rate': round(hit_rate, 1),
            'pool_rankings': pool_rankings,
        })
        
        return context

class PoolListView(LoginRequiredMixin, ListView):
    model = Pool
    template_name = 'pools/pool_list.html'
    context_object_name = 'pools'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Pool.objects.select_related(
            'competition', 
            'competition__sport', 
            'owner'
        ).prefetch_related('participants').annotate(
            participant_count=Count('participants'),
            total_bets=Count('bet')
        )
        
        # Filtros
        search = self.request.GET.get('search', '').strip()
        sport = self.request.GET.get('sport', '')
        status = self.request.GET.get('status', '')
        date_filter = self.request.GET.get('date_filter', '')
        entry_fee_filter = self.request.GET.get('entry_fee', '')
        
        # Filtro de busca por nome
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(competition__name__icontains=search) |
                Q(owner__username__icontains=search)
            )
        
        # Filtro por esporte
        if sport and sport.isdigit():
            queryset = queryset.filter(competition__sport__id=sport)
        
        # Filtro por status
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por taxa de entrada
        if entry_fee_filter:
            if entry_fee_filter == 'free':
                queryset = queryset.filter(entry_fee=0)
            elif entry_fee_filter == 'paid':
                queryset = queryset.filter(entry_fee__gt=0)
        
        # Filtro por data de criação
        if date_filter:
            today = timezone.now().date()
            if date_filter == 'today':
                queryset = queryset.filter(created_at__date=today)
            elif date_filter == 'week':
                week_ago = today - timedelta(days=7)
                queryset = queryset.filter(created_at__date__gte=week_ago)
            elif date_filter == 'month':
                month_ago = today - timedelta(days=30)
                queryset = queryset.filter(created_at__date__gte=month_ago)
        
        # Ordenação
        order_by = self.request.GET.get('order_by', '-created_at')
        valid_orders = [
            '-created_at', 'created_at', 'name', '-name', 
            'status', '-status', 'participant_count', '-participant_count',
            'entry_fee', '-entry_fee'
        ]
        if order_by in valid_orders:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Opções para filtros
        from .models import Sport
        context['sports'] = Sport.objects.all().order_by('name')
        
        # Valores atuais dos filtros
        context['current_search'] = self.request.GET.get('search', '')
        context['current_sport'] = self.request.GET.get('sport', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_date_filter'] = self.request.GET.get('date_filter', '')
        context['current_entry_fee'] = self.request.GET.get('entry_fee', '')
        context['current_order'] = self.request.GET.get('order_by', '-created_at')
        
        # Estatísticas para o usuário
        context['user_stats'] = {
            'owned_pools': Pool.objects.filter(owner=user).count(),
            'joined_pools': Pool.objects.filter(participants=user).exclude(owner=user).count(),
            'total_pools': Pool.objects.filter(Q(owner=user) | Q(participants=user)).distinct().count()
        }
        
        # Status choices para o template
        context['status_choices'] = Pool.STATUS_CHOICES
        
        # Entry fee choices
        context['entry_fee_choices'] = [
            ('', 'Todas as taxas'),
            ('free', 'Gratuitos'),
            ('paid', 'Pagos')
        ]
        
        # Date filter choices
        context['date_filter_choices'] = [
            ('', 'Qualquer data'),
            ('today', 'Hoje'),
            ('week', 'Última semana'),
            ('month', 'Último mês')
        ]
        
        # Order choices
        context['order_choices'] = [
            ('-created_at', 'Mais recentes'),
            ('created_at', 'Mais antigos'),
            ('name', 'Nome A-Z'),
            ('-name', 'Nome Z-A'),
            ('-participant_count', 'Mais participantes'),
            ('participant_count', 'Menos participantes'),
            ('-entry_fee', 'Maior taxa'),
            ('entry_fee', 'Menor taxa')
        ]
        
        # Para cada pool, adicionar informações extras
        pools_with_info = []
        for pool in context['pools']:
            # Calcular próximas partidas
            upcoming_matches = Match.objects.filter(
                pool=pool,
                finished=False,
                start_time__gte=timezone.now()
            ).count()
            
            pool_info = {
                'pool': pool,
                'participant_count': pool.participant_count,
                'user_is_owner': pool.owner == user,
                'user_is_participant': pool.participants.filter(id=user.id).exists(),
                'can_join': (
                    pool.status == 'open' and 
                    not pool.participants.filter(id=user.id).exists() and 
                    pool.owner != user and
                    pool.visibility == 'public'
                ),
                'has_image': bool(pool.competition and hasattr(pool.competition, 'logo') and pool.competition.logo),
                'upcoming_matches': upcoming_matches,
                'is_full': pool.max_participants and pool.participant_count >= pool.max_participants,
                'entry_fee_display': f'R$ {pool.entry_fee:.2f}' if pool.entry_fee > 0 else 'Gratuito',
                'created_days_ago': (timezone.now().date() - pool.created_at.date()).days
            }
            pools_with_info.append(pool_info)
        
        context['pools_with_info'] = pools_with_info
        
        # Contadores para estatísticas
        total_pools = context['object_list'].count()
        context['results_count'] = total_pools
        context['showing_from'] = 1 if total_pools > 0 else 0
        context['showing_to'] = min(self.paginate_by, total_pools)
        
        if context.get('page_obj'):
            page_obj = context['page_obj']
            context['showing_from'] = (page_obj.number - 1) * self.paginate_by + 1
            context['showing_to'] = min(page_obj.number * self.paginate_by, total_pools)
        
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

class PoolCreateWizardView(LoginRequiredMixin, View):
    """Wizard view for creating pools in 3 steps"""
    template_name = 'pools/pool_create.html'
    
    def get(self, request):
        # Initialize session data if not exists
        if 'pool_wizard_data' not in request.session:
            request.session['pool_wizard_data'] = {
                'step': 1,
                'step_1': {},
                'step_2': {},
                'step_3': {}
            }
        
        step = request.GET.get('step', 1)
        try:
            step = int(step)
            if step not in [1, 2, 3]:
                step = 1
        except ValueError:
            step = 1
        
        request.session['pool_wizard_data']['step'] = step
        
        # Get appropriate form for current step
        if step == 1:
            form = PoolWizardStepOneForm(initial=request.session['pool_wizard_data']['step_1'])
        elif step == 2:
            form = PoolWizardStepTwoForm(initial=request.session['pool_wizard_data']['step_2'])
        else:
            form = PoolWizardStepThreeForm(initial=request.session['pool_wizard_data']['step_3'])
        
        context = {
            'form': form,
            'current_step': step,
            'wizard_data': request.session['pool_wizard_data'],
            'total_steps': 3
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        step = request.session.get('pool_wizard_data', {}).get('step', 1)
        
        if step == 1:
            form = PoolWizardStepOneForm(request.POST, request.FILES)
            if form.is_valid():
                request.session['pool_wizard_data']['step_1'] = form.cleaned_data
                request.session['pool_wizard_data']['step'] = 2
                request.session.modified = True
                return redirect('pools:create_wizard?step=2')
        
        elif step == 2:
            form = PoolWizardStepTwoForm(request.POST)
            if form.is_valid():
                request.session['pool_wizard_data']['step_2'] = form.cleaned_data
                request.session['pool_wizard_data']['step'] = 3
                request.session.modified = True
                return redirect('pools:create_wizard?step=3')
        
        elif step == 3:
            form = PoolWizardStepThreeForm(request.POST)
            if form.is_valid():
                request.session['pool_wizard_data']['step_3'] = form.cleaned_data
                # Create the pool
                return self.create_pool(request)
        
        # If form is not valid, render with errors
        context = {
            'form': form,
            'current_step': step,
            'wizard_data': request.session['pool_wizard_data'],
            'total_steps': 3
        }
        
        return render(request, self.template_name, context)
    
    def create_pool(self, request):
        """Create the pool from wizard data"""
        wizard_data = request.session['pool_wizard_data']
        
        try:
            # Extract data from all steps
            step_1 = wizard_data['step_1']
            step_2 = wizard_data['step_2']
            step_3 = wizard_data['step_3']
            
            # Create the pool
            pool = Pool.objects.create(
                name=step_1['name'],
                description=step_1.get('description', ''),
                competition=step_1['competition'],
                owner=request.user,
                entry_fee=step_2.get('entry_fee', 0),
                max_participants=step_2.get('max_participants', 0),
                betting_deadline=step_2.get('betting_deadline'),
                visibility=step_2.get('visibility', 'public'),
                exact_score_points=step_2.get('exact_score_points', 10),
                correct_difference_points=step_2.get('correct_difference_points', 5),
                correct_winner_points=step_2.get('correct_winner_points', 3)
            )
            
            # Add owner as participant
            Participation.objects.create(
                user=request.user,
                pool=pool,
                payment_status='paid'
            )
            
            # Handle invitations if provided
            if step_3.get('invite_emails'):
                self.send_invitations(pool, step_3['invite_emails'], step_3.get('custom_message', ''))
            
            # Clear wizard data
            del request.session['pool_wizard_data']
            request.session.modified = True
            
            messages.success(request, f"Bolão '{pool.name}' criado com sucesso!")
            return redirect('pools:create_success', slug=pool.slug)
            
        except Exception as e:
            messages.error(request, f"Erro ao criar bolão: {str(e)}")
            return redirect('pools:create_wizard?step=1')
    
    def send_invitations(self, pool, emails_string, custom_message):
        """Send email invitations"""
        emails = [email.strip() for email in emails_string.split(',') if email.strip()]
        
        for email in emails:
            try:
                # Create invitation record
                Invitation.objects.create(
                    pool=pool,
                    email=email,
                    invited_by=pool.owner,
                    message=custom_message
                )
                # Here you would send the actual email
                # send_invitation_email(invitation)
            except Exception as e:
                print(f"Error sending invitation to {email}: {e}")

class PoolCreateSuccessView(LoginRequiredMixin, TemplateView):
    """Success page after pool creation"""
    template_name = 'pools/pool_create_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pool = get_object_or_404(Pool, slug=kwargs['slug'], owner=self.request.user)
        context['pool'] = pool
        
        # Generate sharing links
        context['share_link'] = self.request.build_absolute_uri(
            reverse('pools:detail', kwargs={'slug': pool.slug})
        )
        context['whatsapp_link'] = f"https://wa.me/?text=Participe do meu bolão '{pool.name}'! {context['share_link']}"
        
        return context

class PoolDetailView(DetailView):
    model = Pool
    template_name = 'pools/pool_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pool = self.get_object()
        user = self.request.user
        
        # Informações básicas do bolão
        context['is_owner'] = pool.owner == user
        
        # Buscar participações com ranking ordenado por pontos
        participations = pool.participation_set.all().select_related('user').annotate(
            total_bets=Count('user__bet', filter=Q(user__bet__match__pool=pool)),
            accuracy=Case(
                When(total_bets=0, then=Value(0)),
                default=(Count('user__bet', filter=Q(
                    user__bet__match__pool=pool,
                    user__bet__match__finished=True,
                    user__bet__points_earned__gt=0
                )) * 100.0 / Count('user__bet', filter=Q(
                    user__bet__match__pool=pool,
                    user__bet__match__finished=True
                )))
            )
        ).order_by('-points')
        context['participants'] = participations
        context['participants_count'] = participations.count()
        
        # Verificar se o usuário atual é um participante
        user_participation = None
        if user.is_authenticated:
            try:
                user_participation = participations.get(user=user)
                context['is_participant'] = True
                context['user_participation'] = user_participation
                context['user_position'] = list(participations).index(user_participation) + 1
            except Participation.DoesNotExist:
                context['is_participant'] = False
        
        # Próximas partidas da competição (próximos 7 dias)
        upcoming_matches = Match.objects.filter(
            pool=pool,
            finished=False,
            start_time__gte=timezone.now(),
            start_time__lte=timezone.now() + timedelta(days=30)  # Aumentado para 30 dias
        ).select_related('home_team', 'away_team').order_by('start_time')[:10]
        context['upcoming_matches'] = upcoming_matches
        
        # Apostas do usuário (todas)
        if user.is_authenticated and context['is_participant']:
            user_bets = Bet.objects.filter(
                user=user,
                match__pool=pool
            ).select_related('match', 'match__home_team', 'match__away_team').order_by('-match__start_time')
            context['user_bets'] = user_bets
            
            # Apostas do usuário indexadas por match_id para template
            context['user_bets_dict'] = {bet.match_id: bet for bet in user_bets}
        else:
            context['user_bets'] = []
            context['user_bets_dict'] = {}
        
        # Estatísticas do pool
        total_matches = Match.objects.filter(pool=pool).count()
        finished_matches = Match.objects.filter(pool=pool, finished=True).count()
        context['pool_stats'] = {
            'total_matches': total_matches,
            'finished_matches': finished_matches,
            'remaining_matches': total_matches - finished_matches,
            'progress_percentage': (finished_matches / total_matches * 100) if total_matches > 0 else 0
        }
        
        # Estatísticas do usuário (se participante)
        if user_participation:
            user_bets_total = Bet.objects.filter(user=user, match__pool=pool).count()
            user_finished_bets = Bet.objects.filter(
                user=user, 
                match__pool=pool, 
                match__finished=True
            )
            user_correct_bets = user_finished_bets.filter(points_earned__gt=0).count()
            finished_bets_count = user_finished_bets.count()
            
            context['user_stats'] = {
                'total_bets': user_bets_total,
                'correct_bets': user_correct_bets,
                'accuracy_rate': (user_correct_bets / finished_bets_count * 100) if finished_bets_count > 0 else 0,
                'total_points': user_participation.points,
                'average_points': user_participation.points / finished_bets_count if finished_bets_count > 0 else 0
            }
        
        # Top 3 para destaque
        context['top_3'] = participations[:3]
        
        # Ranking completo com posições
        ranking_data = []
        for idx, participation in enumerate(participations):
            ranking_data.append({
                'position': idx + 1,
                'participation': participation,
                'is_current_user': participation.user == user
            })
        context['ranking_data'] = ranking_data
        
        # Dados para contadores
        context['total_points'] = participations.aggregate(
            total=Sum('points')
        )['total'] or 0
        
        context['total_bets'] = Bet.objects.filter(match__pool=pool).count()
        
        # Dados para tabs
        context['active_tab'] = self.request.GET.get('tab', 'ranking')
        
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
    
    def get(self, request, **_kwargs):
        pool = self.get_pool()
        
        # Verifica se o usuário já participa
        if Participation.objects.filter(user=request.user, pool=pool).exists():
            messages.info(request, 'Você já participa deste bolão.')
            return redirect('pools:detail', slug=pool.slug)
            
        form = PoolJoinForm(initial={'pool': pool})
        return render(request, self.template_name, {'pool': pool, 'form': form})
    
    def post(self, request, **_kwargs):
        pool = self.get_pool()
        
        # Verificar novamente se o usuário já participa (proteção contra duplicate entry)
        if Participation.objects.filter(user=request.user, pool=pool).exists():
            messages.info(request, 'Você já participa deste bolão.')
            return redirect('pools:detail', slug=pool.slug)
        
        # Verificar se o bolão ainda está aberto
        if pool.status != 'open':
            messages.error(request, 'Este bolão não está mais disponível para participação.')
            return redirect('pools:detail', slug=pool.slug)
        
        # Verificar limite de participantes
        if pool.max_participants and pool.get_participant_count() >= pool.max_participants:
            messages.error(request, 'Este bolão já atingiu o limite máximo de participantes.')
            return redirect('pools:detail', slug=pool.slug)
        
        form = PoolJoinForm(request.POST)
        
        # Verificar se o formulário é válido antes de acessar cleaned_data
        if form.is_valid():
            # Agora podemos acessar cleaned_data com segurança
            payment_method = form.cleaned_data.get('payment_method')
            
            try:
                # Criar participação com proteção adicional
                participation, created = Participation.objects.get_or_create(
                    user=request.user,
                    pool=pool,
                    defaults={
                        'payment_method': payment_method,
                        'payment_status': 'pending'
                    }
                )
                
                if created:
                    messages.success(request, f'Você se juntou ao bolão {pool.name}!')
                else:
                    messages.info(request, 'Você já participa deste bolão.')
                
                return redirect('pools:detail', slug=pool.slug)
                
            except IntegrityError:
                # Fallback em caso de erro de integridade
                messages.info(request, 'Você já participa deste bolão.')
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

def calculate_user_streak(user, pool):
    """Calcula a sequência atual de acertos do usuário"""
    recent_bets = Bet.objects.filter(
        user=user,
        pool=pool,
        match__finished=True
    ).order_by('-match__start_time')[:10]  # Últimas 10 apostas
    
    streak = 0
    for bet in recent_bets:
        if bet.points_earned > 0:
            streak += 1
        else:
            break
    
    return streak

def calculate_user_trend(user, pool):
    """Calcula a tendência do usuário (alta, baixa, estável)"""
    recent_bets = Bet.objects.filter(
        user=user,
        pool=pool,
        match__finished=True
    ).order_by('-match__start_time')[:6]  # Últimas 6 apostas
    
    if len(recent_bets) < 3:
        return 'stable'
    
    first_half = recent_bets[3:]  # 3 mais antigas
    second_half = recent_bets[:3]  # 3 mais recentes
    
    first_half_avg = sum(bet.points_earned for bet in first_half) / len(first_half)
    second_half_avg = sum(bet.points_earned for bet in second_half) / len(second_half)
    
    if second_half_avg > first_half_avg * 1.2:
        return 'up'
    elif second_half_avg < first_half_avg * 0.8:
        return 'down'
    else:
        return 'stable'

def pool_ranking(request, slug):
    """Exibe o ranking geral de participantes do bolão com análise avançada"""
    pool = get_object_or_404(Pool, slug=slug)
    
    # Verifica se o usuário tem acesso
    if pool.visibility == 'private' and request.user not in pool.participants.all() and request.user != pool.owner:
        messages.error(request, "Você não tem acesso a este bolão.")
        return redirect('pools:discover')
    
    # Busca todos os participantes com estatísticas detalhadas
    participants = Participation.objects.filter(pool=pool).select_related('user').annotate(
        total_bets=Count('user__bet', filter=Q(user__bet__match__pool=pool)),
        correct_bets=Count('user__bet', filter=Q(
            user__bet__match__pool=pool,
            user__bet__match__finished=True,
            user__bet__points_earned__gt=0
        )),
        total_finished_bets=Count('user__bet', filter=Q(
            user__bet__match__pool=pool,
            user__bet__match__finished=True
        )),
        accuracy=Case(
            When(total_finished_bets=0, then=Value(0)),
            default=(F('correct_bets') * 100.0 / F('total_finished_bets'))
        ),
        avg_points=Avg('user__bet__points_earned', filter=Q(
            user__bet__match__pool=pool,
            user__bet__match__finished=True
        ))
    ).order_by('-points')
    
    # Calcular estatísticas especiais
    best_performer = participants.first()
    highest_accuracy = participants.order_by('-accuracy').first()
    total_points = participants.aggregate(total=Sum('points'))['total'] or 0
    
    # Calcular sequências e tendências
    for participant in participants:
        participant.streak = calculate_user_streak(participant.user, pool)
        participant.trend = calculate_user_trend(participant.user, pool)
    
    # Top participantes para o gráfico (máximo 5)
    top_participants = list(participants[:5])
    
    # Dados para gráfico de evolução
    matches = Match.objects.filter(pool=pool, finished=True).order_by('start_time')
    round_labels = [f"R{i+1}" for i in range(len(matches))]
    
    # Calcular histórico de pontos por rodada para cada participante
    for participant in top_participants:
        points_history = []
        cumulative_points = 0
        
        for match in matches:
            try:
                bet = Bet.objects.get(user=participant.user, match=match, pool=pool)
                cumulative_points += bet.points_earned
            except Bet.DoesNotExist:
                pass
            points_history.append(cumulative_points)
        
        participant.points_history = points_history
    
    # Calcular sequência mais longa
    longest_streak = {'streak': 0, 'user': None}
    for participant in participants:
        if participant.streak > longest_streak['streak']:
            longest_streak = {'streak': participant.streak, 'user': participant.user}
    
    # Opções de rodadas para filtro
    round_options = list(range(1, len(matches) + 1))
    
    context = {
        'pool': pool,
        'participants': participants,
        'is_owner': request.user == pool.owner,
        'is_participant': Participation.objects.filter(pool=pool, user=request.user).exists() if request.user.is_authenticated else False,
        'active_tab': 'ranking',
        'now': timezone.now(),
        
        # Estatísticas
        'best_performer': best_performer,
        'highest_accuracy': highest_accuracy,
        'longest_streak': longest_streak,
        'total_points': total_points,
        
        # Dados para gráfico
        'top_participants': top_participants,
        'round_labels': round_labels,
        'round_options': round_options,
    }
    
    # Se for uma requisição AJAX, retorna apenas os dados
    if request.GET.get('ajax'):
        return JsonResponse({
            'participants': [
                {
                    'user': p.user.username,
                    'points': p.points,
                    'accuracy': float(p.accuracy or 0),
                    'total_bets': p.total_bets,
                    'streak': p.streak,
                    'trend': p.trend,
                }
                for p in participants
            ],
            'updated': True
        })
    
    return render(request, 'pools/pool_ranking.html', context)

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
            user = User.objects.get(id=bet['user'])
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
    
    # Verificar se o bolão ainda está aberto
    if invitation.pool.status != 'open':
        messages.error(request, 'Este bolão não está mais disponível para participação.')
        return redirect('pools:detail', slug=invitation.pool.slug)
    
    # Verificar limite de participantes
    if invitation.pool.max_participants and invitation.pool.get_participant_count() >= invitation.pool.max_participants:
        messages.error(request, 'Este bolão já atingiu o limite máximo de participantes.')
        return redirect('pools:detail', slug=invitation.pool.slug)
    
    try:
        # Criar participação com proteção adicional
        participation, created = Participation.objects.get_or_create(
            user=request.user,
            pool=invitation.pool,
            defaults={
                'payment_status': 'pending' if invitation.pool.entry_fee > 0 else 'paid'
            }
        )
        
        if created:
            invitation.status = 'accepted'
            invitation.save()
            messages.success(request, f"Você entrou no bolão {invitation.pool.name}!")
        else:
            invitation.status = 'accepted'
            invitation.save()
            messages.info(request, "Você já está participando deste bolão.")
            
    except IntegrityError:
        # Fallback em caso de erro de integridade
        invitation.status = 'accepted'
        invitation.save()
        messages.info(request, "Você já está participando deste bolão.")
    
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
    # Funcionalidade desabilitada temporariamente
    messages.error(request, "Funcionalidade temporariamente indisponível.")
    return redirect('pools:create')

def create_tournament_pool(request, tournament_slug):
    """Cria um bolão para um torneio específico"""
    # Funcionalidade desabilitada temporariamente
    # O parâmetro tournament_slug não é usado nesta implementação simplificada
    _ = tournament_slug  # Evita warning de variável não utilizada
    messages.error(request, "Funcionalidade temporariamente indisponível.")
    return redirect('pools:create')


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
            # Se não há partidas futuras, usar uma existente para demonstração
            match = Match.objects.first()
            if match:
                # Ajustar data para futuro
                match.start_time = timezone.now() + timedelta(hours=24)
                match.finished = False
                match.save()
    
    # Pool opcional para teste
    pool = None
    if pool_id:
        pool = get_object_or_404(Pool, id=pool_id)
    
    # Verificar se o usuário já tem uma aposta nesta partida
    existing_bet = None
    if pool and match:
        try:
            existing_bet = Bet.objects.get(
                user=request.user,
                match=match,
                participation__pool=pool
            )
        except Bet.DoesNotExist:
            pass
    
    if request.method == 'POST' and match:
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
            
            # Redirecionar para o dashboard
            return redirect('pools:dashboard')
        else:
            messages.error(request, '❌ Erro ao processar a aposta. Verifique os dados.')
    else:
        form = BetForm(
            instance=existing_bet,
            match=match,
            pool=pool,
            user=request.user
        ) if match else None
    
    context = {
        'form': form,
        'match': match,
        'pool': pool,
        'existing_bet': existing_bet,
        'now': timezone.now(),
    }
    
    return render(request, 'pools/bet_form_simple.html', context)
