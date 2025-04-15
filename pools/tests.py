from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from pools.models import Pool, Match, Bet, Competition, Sport, Participation
from pools.forms import BetForm
from pools.views import calculate_bet_points, bet_match
from pools.mixins import PoolUserAccessMixin
from datetime import timedelta
import uuid

User = get_user_model()

# Corrigir SimpleTest para garantir que seja executado
class SimpleTest(TestCase):
    """Teste simples para verificar se o framework de testes está funcionando"""
    
    def test_basic_addition(self):
        """Um teste simples que sempre passa"""
        self.assertEqual(1 + 1, 2)
        print("Teste simples executado com sucesso!")


class BetModelTest(TestCase):
    """Testes para o modelo Bet"""
    
    def setUp(self):
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        
        # Criar esporte
        self.sport = Sport.objects.create(name='Futebol', icon='football')
        
        # Criar competição
        self.competition = Competition.objects.create(
            name='Campeonato Teste',
            sport=self.sport,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90),
            description='Competição para testes',
            is_active=True
        )
        
        # Criar bolão
        self.pool = Pool.objects.create(
            name='Bolão de Teste',
            owner=self.user,
            competition=self.competition,
            description='Um bolão para testes',
            status='active',
            visibility='public',
            entry_fee=0,
            max_participants=100,
            betting_deadline=timezone.now() + timedelta(days=1),
            invitation_key=uuid.uuid4()
        )
        self.pool.participants.add(self.user)
        
        # Criar partida futura (nota: home_team e away_team são strings, não objetos)
        self.future_match = Match.objects.create(
            competition=self.competition,
            home_team='Time Casa',  # String, não um objeto Team
            away_team='Time Fora',  # String, não um objeto Team
            start_time=timezone.now() + timedelta(days=1)
        )
        
        # Criar partida finalizada
        self.finished_match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=2,
            away_score=1,
            finished=True
        )
    
    def test_create_bet(self):
        """Teste de criação básica de aposta"""
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=self.future_match,
            home_score_bet=2,
            away_score_bet=0
        )
        self.assertEqual(bet.home_score_bet, 2)
        self.assertEqual(bet.away_score_bet, 0)
        self.assertEqual(bet.user, self.user)
        
    def test_unique_constraint(self):
        """Teste da restrição unique_together"""
        # Criar primeira aposta
        Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=self.future_match,
            home_score_bet=2,
            away_score_bet=0
        )
        
        # Tentar criar outra aposta para a mesma combinação
        with self.assertRaises(Exception):
            Bet.objects.create(
                user=self.user,
                pool=self.pool,
                match=self.future_match,
                home_score_bet=3,
                away_score_bet=1
            )
    
    def test_bet_str_representation(self):
        """Teste da representação string do modelo Bet"""
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=self.future_match,
            home_score_bet=2,
            away_score_bet=0
        )
        expected = f"{self.user.username}: {self.future_match.home_team} {bet.home_score_bet} x {bet.away_score_bet} {self.future_match.away_team}"
        self.assertEqual(str(bet), expected)
    
    def test_bet_points_earned(self):
        """Teste do campo points_earned"""
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=self.finished_match,
            home_score_bet=2,
            away_score_bet=1,
            points_earned=10
        )
        self.assertEqual(bet.points_earned, 10)


class BetFormTests(TestCase):
    """Testes para o formulário de apostas"""
    
    def test_bet_form_valid_data(self):
        """Teste com dados válidos"""
        form_data = {
            'home_score_bet': 2,
            'away_score_bet': 1
        }
        form = BetForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_bet_form_negative_score(self):
        """Teste com pontuação negativa (inválido)"""
        form_data = {
            'home_score_bet': -1,
            'away_score_bet': 1
        }
        form = BetForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_bet_form_empty_data(self):
        """Teste com dados ausentes"""
        form = BetForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Dois campos são obrigatórios
    
    def test_bet_form_widget_attrs(self):
        """Teste de atributos personalizados do widget"""
        form = BetForm()
        self.assertEqual(form.fields['home_score_bet'].widget.attrs.get('min'), '0')
        self.assertEqual(form.fields['away_score_bet'].widget.attrs.get('class'), 'form-control score-input')


class BetViewTests(TestCase):
    """Testes para a view de apostas"""
    
    def setUp(self):
        # Configuração básica necessária
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.factory = RequestFactory()
        
        # Criar os objetos necessários
        self.sport = Sport.objects.create(name='Futebol', icon='football')
        self.competition = Competition.objects.create(
            name='Torneio Teste',
            sport=self.sport,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90)
        )
        
        self.pool = Pool.objects.create(
            name='Bolão de Teste',
            description='Descrição teste',
            owner=self.user,
            competition=self.competition,
            status='active',
            visibility='public',
            betting_deadline=timezone.now() + timedelta(days=7)
        )
        self.pool.participants.add(self.user)
        
        # Criar partidas para testar
        self.future_match = Match.objects.create(
            competition=self.competition,
            home_team='Time Casa',
            away_team='Time Fora',
            start_time=timezone.now() + timedelta(days=1)
        )
        
        self.past_match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(hours=1),
            finished=True,
            home_score=2,
            away_score=1
        )
        
        # URLs para os testes
        self.bet_url = reverse('pools:bet_match', args=[self.pool.id, self.future_match.id])
        self.past_bet_url = reverse('pools:bet_match', args=[self.pool.id, self.past_match.id])
    
    def test_bet_view_requires_login(self):
        """Teste se a view requer login"""
        response = self.client.get(self.bet_url)
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={self.bet_url}')
        
    def test_bet_view_get(self):
        """Teste de acesso GET à página de apostas"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.bet_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pools/bet_form.html')
        
    def test_bet_view_past_match(self):
        """Teste de acesso a partida que já começou"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.past_bet_url)
        # Deve redirecionar por causa do prazo expirado
        self.assertRedirects(response, reverse('pools:detail', args=[self.pool.id]))
        
    def test_bet_view_nonparticipant_access(self):
        """Teste de acesso por usuário que não participa do bolão"""
        # Criar usuário que não participa
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Tentar acessar com outro usuário
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(self.bet_url)
        
        # Deve redirecionar para detalhes do bolão
        self.assertRedirects(response, reverse('pools:detail', args=[self.pool.id]))
    
    def test_bet_view_post_success(self):
        """Teste de criação de aposta bem-sucedida"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.bet_url, {
            'home_score_bet': 3,
            'away_score_bet': 1
        })
        self.assertRedirects(response, reverse('pools:detail', args=[self.pool.id]))
        
        # Verificar se a aposta foi criada
        bet = Bet.objects.filter(
            user=self.user,
            match=self.future_match,
            pool=self.pool
        ).first()
        self.assertIsNotNone(bet)
        self.assertEqual(bet.home_score_bet, 3)
        self.assertEqual(bet.away_score_bet, 1)
    
    def test_mixins_pool_user_access(self):
        """Teste do mixin de acesso ao bolão"""
        mixin = PoolUserAccessMixin()
        
        # Simular request
        request = self.factory.get('/')
        request.user = self.user
        
        # Simular messages
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # O usuário tem acesso
        response = mixin.test_func(request, self.pool.id)
        self.assertTrue(response)
        
        # Criar usuário sem acesso
        other_user = User.objects.create_user('noparticipant', 'no@example.com', 'password123')
        request.user = other_user
        
        # O usuário não tem acesso
        response = mixin.test_func(request, self.pool.id)
        self.assertFalse(response)


class PointCalculationTests(TestCase):
    """Testes para o cálculo de pontuação"""
    
    def setUp(self):
        # Criar objetos básicos para testes
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.sport = Sport.objects.create(name='Futebol', icon='football')
        self.competition = Competition.objects.create(
            name='Torneio Teste',
            sport=self.sport,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=90)
        )
        
        self.pool = Pool.objects.create(
            name='Bolão de Teste',
            description='Descrição teste',
            owner=self.user,
            competition=self.competition,
            status='active'
        )
        
    def test_bet_points_exact_score(self):
        """Teste de pontuação para placar exato (10 pontos)"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=2,
            away_score=1,
            finished=True
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=2,
            away_score_bet=1
        )
        
        points = calculate_bet_points(bet)
        self.assertEqual(points, 10)
        
    def test_bet_points_correct_winner_and_difference(self):
        """Teste de pontuação para vencedor e diferença corretos (5 pontos)"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=3,
            away_score=1,
            finished=True
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=2,
            away_score_bet=0
        )
        
        points = calculate_bet_points(bet)
        self.assertEqual(points, 5)
        
    def test_bet_points_correct_winner_only(self):
        """Teste de pontuação para apenas o vencedor correto (3 pontos)"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=2,
            away_score=0,
            finished=True
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=1,
            away_score_bet=0
        )
        
        points = calculate_bet_points(bet)
        self.assertEqual(points, 3)
        
    def test_bet_points_draw(self):
        """Teste para aposta em empate"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=1,
            away_score=1,
            finished=True
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=0,
            away_score_bet=0
        )
        
        # É empate, mas com placar diferente, então 3 pontos
        points = calculate_bet_points(bet)
        self.assertEqual(points, 3)
    
    def test_bet_points_match_not_finished(self):
        """Teste para partida não finalizada"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(hours=1),
            finished=False
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=2,
            away_score_bet=1
        )
        
        points = calculate_bet_points(bet)
        self.assertEqual(points, 0)
    
    def test_bet_points_wrong_prediction(self):
        """Teste para previsão completamente errada"""
        match = Match.objects.create(
            competition=self.competition,
            home_team='Time A',
            away_team='Time B',
            start_time=timezone.now() - timedelta(days=1),
            home_score=0,
            away_score=2,
            finished=True
        )
        
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=match,
            home_score_bet=2,
            away_score_bet=0
        )
        
        points = calculate_bet_points(bet)
        self.assertEqual(points, 0)
