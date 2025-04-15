from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from pools.models import Pool, Match, Bet, Team, Competition
from pools.forms import BetForm
from datetime import timedelta

User = get_user_model()

class BetModelTest(TestCase):
    """Testes para o modelo Bet"""
    
    def setUp(self):
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        
        # Criar times
        self.team_home = Team.objects.create(name='Time Casa', abbreviation='CAS')
        self.team_away = Team.objects.create(name='Time Fora', abbreviation='FOR')
        
        # Criar competição
        self.competition = Competition.objects.create(name='Campeonato Teste')
        
        # Criar bolão
        self.pool = Pool.objects.create(
            name='Bolão de Teste',
            owner=self.user,
            competition=self.competition,
            description='Um bolão para testes',
        )
        self.pool.participants.add(self.user)
        
        # Criar partida futura
        self.future_match = Match.objects.create(
            home_team=self.team_home,
            away_team=self.team_away,
            competition=self.competition,
            start_time=timezone.now() + timedelta(days=1),
        )
        
        # Criar partida finalizada
        self.finished_match = Match.objects.create(
            home_team=self.team_home,
            away_team=self.team_away,
            competition=self.competition,
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


class BetViewTest(TestCase):
    """Testes para a view bet_match"""
    
    def setUp(self):
        # Criar usuário de teste
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            email='other@example.com', 
            password='testpass123'
        )
        
        # Criar times
        self.team_home = Team.objects.create(name='Time Casa', abbreviation='CAS')
        self.team_away = Team.objects.create(name='Time Fora', abbreviation='FOR')
        
        # Criar competição
        self.competition = Competition.objects.create(name='Campeonato Teste')
        
        # Criar bolão
        self.pool = Pool.objects.create(
            name='Bolão de Teste',
            owner=self.user,
            competition=self.competition,
            description='Um bolão para testes',
        )
        self.pool.participants.add(self.user)
        
        # Criar partida futura
        self.future_match = Match.objects.create(
            home_team=self.team_home,
            away_team=self.team_away,
            competition=self.competition,
            start_time=timezone.now() + timedelta(days=1),
        )
        
        # Criar partida que já começou
        self.started_match = Match.objects.create(
            home_team=self.team_home,
            away_team=self.team_away,
            competition=self.competition,
            start_time=timezone.now() - timedelta(hours=1),
        )
        
        # URL para apostar
        self.bet_url = reverse('pools:bet_match', args=[self.pool.id, self.future_match.id])
        self.bet_started_url = reverse('pools:bet_match', args=[self.pool.id, self.started_match.id])
        
    def test_login_required(self):
        """Teste de acesso sem login"""
        response = self.client.get(self.bet_url)
        # Deve redirecionar para página de login
        self.assertRedirects(
            response, 
            f'/login/?next={self.bet_url}'
        )
    
    def test_non_participant_access(self):
        """Teste para usuário que não é participante"""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.get(self.bet_url)
        # Deve redirecionar para detalhe do bolão
        self.assertRedirects(
            response, 
            reverse('pools:detail', args=[self.pool.id])
        )
    
    def test_match_already_started(self):
        """Teste para partida que já começou"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.bet_started_url)
        # Deve redirecionar para detalhe do bolão
        self.assertRedirects(
            response, 
            reverse('pools:detail', args=[self.pool.id])
        )
    
    def test_create_new_bet(self):
        """Teste para criação de nova aposta"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            self.bet_url, 
            {'home_score_bet': 2, 'away_score_bet': 1}
        )
        # Deve redirecionar para detalhe do bolão após sucesso
        self.assertRedirects(
            response, 
            reverse('pools:detail', args=[self.pool.id])
        )
        
        # Verificar se a aposta foi criada
        bet_exists = Bet.objects.filter(
            user=self.user,
            pool=self.pool,
            match=self.future_match,
            home_score_bet=2,
            away_score_bet=1
        ).exists()
        self.assertTrue(bet_exists)
    
    def test_update_existing_bet(self):
        """Teste para atualização de aposta existente"""
        # Criar aposta inicial
        bet = Bet.objects.create(
            user=self.user,
            pool=self.pool,
            match=self.future_match,
            home_score_bet=1,
            away_score_bet=1
        )
        
        # Fazer login e atualizar a aposta
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            self.bet_url, 
            {'home_score_bet': 3, 'away_score_bet': 0}
        )
        
        # Recarregar a aposta do banco de dados
        bet.refresh_from_db()
        
        # Verificar se a aposta foi atualizada
        self.assertEqual(bet.home_score_bet, 3)
        self.assertEqual(bet.away_score_bet, 0)