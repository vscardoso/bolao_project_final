from django.core.management.base import BaseCommand
from pools.models import Match, Game, Team
from django.db import transaction

class Command(BaseCommand):
    help = 'Corrige relacionamentos entre Match e Game/Team'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando correção de relacionamentos...')
        
        # 1. Corrigir Matches sem teams
        matches_sem_team = Match.objects.filter(home_team__isnull=True)
        self.stdout.write(f'Encontrados {matches_sem_team.count()} matches sem team')
        
        fixed_matches = 0
        for match in matches_sem_team:
            if match.related_game:
                game = match.related_game
                match.home_team = game.home_team
                match.away_team = game.away_team
                match.save()
                fixed_matches += 1
        
        self.stdout.write(f'Corrigidos {fixed_matches} matches com teams')
        
        # 2. Criar relacionamentos Game->Match baseado em times e scores
        games_finalizados = Game.objects.filter(finished=True)
        created_relations = 0
        
        for game in games_finalizados:
            # Buscar matches que não têm related_game mas têm os mesmos times
            matches_orfaos = Match.objects.filter(
                related_game__isnull=True,
                home_team=game.home_team,
                away_team=game.away_team
            )
            
            for match in matches_orfaos:
                match.related_game = game
                match.home_score = game.home_score
                match.away_score = game.away_score
                match.finished = True
                match.result = match.calculate_result()
                match.save()
                created_relations += 1
        
        self.stdout.write(f'Criados {created_relations} relacionamentos Game->Match')
        
        # 3. Recalcular pontos das apostas
        from pools.models import Bet
        
        updated_bets = 0
        for match in Match.objects.filter(finished=True):
            bets = Bet.objects.filter(match=match)
            for bet in bets:
                # Recalcular pontos
                old_points = bet.points_earned
                bet.calculate_points()
                bet.save()
                if bet.points_earned != old_points:
                    updated_bets += 1
        
        self.stdout.write(f'Recalculados pontos de {updated_bets} apostas')
        
        # 4. Relatório final
        self.stdout.write('\n=== RELATÓRIO FINAL ===')
        self.stdout.write(f'Matches com teams: {Match.objects.filter(home_team__isnull=False).count()}')
        self.stdout.write(f'Matches com related_game: {Match.objects.filter(related_game__isnull=False).count()}')
        self.stdout.write(f'Matches finalizados: {Match.objects.filter(finished=True).count()}')
        self.stdout.write(f'Total de apostas: {Bet.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('Correção de relacionamentos concluída!'))