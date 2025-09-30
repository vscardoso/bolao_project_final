from django.core.management.base import BaseCommand
from pools.models import Match, Game, Team, Pool, Competition
from django.db import transaction

class Command(BaseCommand):
    help = 'Cria matches reais baseados nos games da API'

    def handle(self, *args, **options):
        self.stdout.write('Criando matches reais baseados nos games...')
        
        # Buscar ou criar um pool de teste
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Primeiro, criar um usuário owner
        owner, created = User.objects.get_or_create(
            username='pool_owner',
            defaults={
                'email': 'owner@example.com',
                'first_name': 'Pool',
                'last_name': 'Owner'
            }
        )
        
        if created:
            owner.set_password('ownerpass123')
            owner.save()
            self.stdout.write(f'Usuário owner criado: {owner.username}')
        
        # Buscar uma competição para associar
        competition = Competition.objects.first()
        if not competition:
            self.stdout.write(self.style.ERROR('Nenhuma competição encontrada'))
            return
        
        pool, created = Pool.objects.get_or_create(
            slug='pool-api-test',
            defaults={
                'name': 'Pool API Test',
                'description': 'Pool para testes da API',
                'owner': owner,
                'competition': competition,
                'max_participants': 100,
                'status': 'open',
                'visibility': 'public'
            }
        )
        
        # Limpar matches antigos sem dados
        matches_vazios = Match.objects.filter(home_team__isnull=True)
        deleted_count = matches_vazios.count()
        matches_vazios.delete()
        self.stdout.write(f'Removidos {deleted_count} matches vazios')
        
        # Criar matches baseados nos games finalizados
        games_finalizados = Game.objects.filter(finished=True)[:10]  # Pegar 10 games para teste
        created_matches = 0
        
        for game in games_finalizados:
            # Verificar se já existe match para este game
            existing_match = Match.objects.filter(related_game=game).first()
            if not existing_match:
                match = Match.objects.create(
                    competition=competition,
                    pool=pool,
                    home_team=game.home_team,
                    away_team=game.away_team,
                    start_time=game.datetime,
                    home_score=game.home_score,
                    away_score=game.away_score,
                    finished=game.finished,
                    related_game=game
                )
                match.result = match.calculate_result()
                match.save()
                created_matches += 1
                
                self.stdout.write(f'Match criado: {match.home_team.name} vs {match.away_team.name}')
        
        self.stdout.write(f'Total de matches criados: {created_matches}')
        
        # Criar algumas apostas de teste
        from pools.models import Bet
        
        # Buscar ou criar usuário de teste
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(f'Usuário de teste criado: {user.username}')
        
        # Criar apostas para os matches
        matches = Match.objects.filter(finished=True)[:5]
        created_bets = 0
        
        for match in matches:
            # Verificar se já existe aposta
            existing_bet = Bet.objects.filter(user=user, match=match).first()
            if not existing_bet:
                bet = Bet.objects.create(
                    user=user,
                    match=match,
                    home_score_bet=match.home_score if match.home_score else 1,
                    away_score_bet=match.away_score if match.away_score else 0
                )
                bet.calculate_points()
                bet.save()
                created_bets += 1
                
                self.stdout.write(f'Aposta criada: {bet.home_score_bet}x{bet.away_score_bet} = {bet.points_earned} pontos')
        
        self.stdout.write(f'Total de apostas criadas: {created_bets}')
        
        # Relatório final
        self.stdout.write('\n=== RELATÓRIO FINAL ===')
        self.stdout.write(f'Matches totais: {Match.objects.count()}')
        self.stdout.write(f'Matches finalizados: {Match.objects.filter(finished=True).count()}')
        self.stdout.write(f'Apostas totais: {Bet.objects.count()}')
        self.stdout.write(f'Pool: {pool.name} ({pool.id})')
        
        self.stdout.write(self.style.SUCCESS('Matches reais criados com sucesso!'))