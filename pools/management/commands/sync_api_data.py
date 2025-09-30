from django.core.management.base import BaseCommand
from django.utils import timezone
from pools.models import Championship, Game, Team, Competition, Match, Sport
import requests
from datetime import datetime, timedelta
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Sincroniza dados da API Football-Data (fixtures e resultados)'

    def add_arguments(self, parser):
        parser.add_argument('--competition', type=str, default='BSA', help='Código da competição')
        parser.add_argument('--update-results', action='store_true', help='Atualizar resultados')

    def handle(self, *args, **options):
        api_key = settings.FOOTBALL_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR('FOOTBALL_API_KEY não configurada'))
            return

        headers = {'X-Auth-Token': api_key}
        base_url = 'https://api.football-data.org/v4'
        competition_code = options['competition']

        self.stdout.write(f'Sincronizando {competition_code}...')

        # 1. Buscar competição
        try:
            comp_response = requests.get(f'{base_url}/competitions/{competition_code}', headers=headers)
            comp_data = comp_response.json()
            
            # Buscar ou criar Sport primeiro
            sport, _ = Sport.objects.get_or_create(name='Football', defaults={'description': 'Football/Soccer'})
            
            championship, created = Championship.objects.get_or_create(
                external_api_id=str(comp_data['id']),
                defaults={
                    'name': comp_data['name'], 
                    'season': comp_data.get('currentSeason', {}).get('startDate', '2024')[:4],
                    'sport': sport,
                    'start_date': timezone.now().date(),
                    'end_date': timezone.now().date() + timedelta(days=365),
                }
            )
            self.stdout.write(f'  Competição: {championship.name}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro competição: {e}'))
            return

        # 2. Buscar times
        try:
            teams_response = requests.get(f'{base_url}/competitions/{competition_code}/teams', headers=headers)
            teams_data = teams_response.json()
            
            teams_created = 0
            for team_data in teams_data['teams']:
                _, created = Team.objects.get_or_create(
                    external_api_id=str(team_data['id']),
                    defaults={
                        'name': team_data['name'],
                        'short_name': team_data.get('shortName', team_data['name'][:20]),
                        'code': team_data.get('tla', '')[:3],
                        'championship': championship,  # Adicionar o championship
                    }
                )
                if created:
                    teams_created += 1
            
            self.stdout.write(f'  Times novos: {teams_created}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro times: {e}'))

        # 3. Buscar partidas (últimos 7 dias + próximos 30 dias)
        date_from = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        date_to = (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            matches_response = requests.get(
                f'{base_url}/competitions/{competition_code}/matches',
                headers=headers,
                params={'dateFrom': date_from, 'dateTo': date_to}
            )
            matches_data = matches_response.json()
            
            matches_created = 0
            matches_updated = 0
            
            for match_data in matches_data['matches']:
                if not match_data.get('homeTeam') or not match_data.get('awayTeam'):
                    continue
                
                home_team = Team.objects.filter(external_api_id=str(match_data['homeTeam']['id'])).first()
                away_team = Team.objects.filter(external_api_id=str(match_data['awayTeam']['id'])).first()
                
                if not home_team or not away_team:
                    continue
                
                utc_date = datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00'))
                
                game, created = Game.objects.update_or_create(
                    external_api_id=str(match_data['id']),
                    defaults={
                        'championship': championship,
                        'round': match_data.get('matchday', 1),
                        'home_team': home_team,
                        'away_team': away_team,
                        'datetime': utc_date,
                        'home_score': match_data['score']['fullTime'].get('home'),
                        'away_score': match_data['score']['fullTime'].get('away'),
                        'finished': match_data['status'] == 'FINISHED',
                    }
                )
                
                if created:
                    matches_created += 1
                else:
                    matches_updated += 1
            
            self.stdout.write(f'  Partidas: {matches_created} criadas, {matches_updated} atualizadas')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro partidas: {e}'))

        # 4. Atualizar resultados e calcular pontos
        if options['update_results']:
            self.stdout.write('Atualizando resultados...')
            
            finished_games = Game.objects.filter(
                finished=True,
                home_score__isnull=False,
                away_score__isnull=False,
                championship=championship
            )
            
            updated = 0
            for game in finished_games:
                # Buscar matches relacionados através do related_game
                related_matches = Match.objects.filter(related_game=game)
                
                for match in related_matches:
                    if match.home_score != game.home_score or match.away_score != game.away_score:
                        match.home_score = game.home_score
                        match.away_score = game.away_score
                        match.finished = True
                        match.result = match.calculate_result()
                        match.save()
                        updated += 1
            
            self.stdout.write(self.style.SUCCESS(f'Resultados atualizados: {updated}'))

        self.stdout.write(self.style.SUCCESS('Sincronização concluída'))