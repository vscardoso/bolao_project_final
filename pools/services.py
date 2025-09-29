import requests
import logging
from django.utils import timezone
from datetime import datetime
from .models import Championship, Team, Game, Standing

logger = logging.getLogger(__name__)

def make_naive(dt):
    """Convert timezone-aware datetime to naive datetime"""
    if dt is None:
        return None
    if timezone.is_aware(dt):
        return timezone.make_naive(dt, timezone=timezone.utc)  # timezone.utc (não UTC())
    return dt

class ApiIntegrationService:
    """Base service for sports API integration"""
    
    def __init__(self, championship):
        self.championship = championship
        self.api_key = self._get_api_key()
        
    def _get_api_key(self):
        """Get API key based on provider"""
        from django.conf import settings
        
        api_keys = {
            'football-data': getattr(settings, 'FOOTBALL_DATA_API_KEY', ''),
            'api-football': getattr(settings, 'API_FOOTBALL_API_KEY', ''),
            'sportmonks': getattr(settings, 'SPORTMONKS_API_KEY', ''),
        }
        return api_keys.get(self.championship.api_provider, '')
    
    def update_matches(self):
        """Method to be implemented by subclasses"""
        raise NotImplementedError
    
    def update_standings(self):
        """Method to be implemented by subclasses"""
        raise NotImplementedError
    
    def execute_update(self):
        """Execute complete update"""
        try:
            self.update_matches()
            self.update_standings()
            self.championship.last_update = timezone.now()
            self.championship.save()
            return True
        except Exception as e:
            logger.error(f"Error updating championship {self.championship.name}: {str(e)}")
            return False

class FootballDataApiService(ApiIntegrationService):
    """Integration with football-data.org API"""
    
    base_url = "https://api.football-data.org/v4"
    
    def __init__(self, championship):
        super().__init__(championship)
        self.headers = {"X-Auth-Token": self.api_key}
    
    def update_matches(self):
        """Update championship matches using the API"""
        url = f"{self.base_url}/competitions/{self.championship.external_api_id}/matches"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            for match_data in data['matches']:
                # Get or create teams
                home_team, _ = Team.objects.get_or_create(
                    external_api_id=str(match_data['homeTeam']['id']),
                    championship=self.championship,
                    defaults={
                        'name': match_data['homeTeam']['name'],
                        'short_name': match_data['homeTeam'].get('shortName', ''),
                        'code': match_data['homeTeam'].get('tla', '')[:3],
                    }
                )
                
                away_team, _ = Team.objects.get_or_create(
                    external_api_id=str(match_data['awayTeam']['id']),
                    championship=self.championship,
                    defaults={
                        'name': match_data['awayTeam']['name'],
                        'short_name': match_data['awayTeam'].get('shortName', ''),
                        'code': match_data['awayTeam'].get('tla', '')[:3],
                    }
                )
                
                # Map round
                try:
                    round_number = int(match_data.get('matchday', 0))
                except (ValueError, TypeError):
                    round_number = 0
                
                # Convert date to naive before saving
                match_date = datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00'))
                match_date = make_naive(match_date)
                
                # Create or update game
                game, created = Game.objects.get_or_create(
                    external_api_id=str(match_data['id']),
                    championship=self.championship,
                    defaults={
                        'home_team': home_team,
                        'away_team': away_team,
                        'datetime': match_date,  # Converted date
                        'round': round_number,
                        'venue': match_data.get('venue', ''),
                        'status': self._map_status(match_data['status']),
                    }
                )
                
                if not created:
                    game.datetime = match_date  # Converted date
                    game.status = self._map_status(match_data['status'])
                    game.round = round_number
                    
                # Update score if the game is finished
                if match_data['status'] in ['FINISHED', 'IN_PLAY', 'PAUSED']:
                    game.home_score = match_data['score']['fullTime']['home']
                    game.away_score = match_data['score']['fullTime']['away']
                    
                    if match_data['status'] == 'FINISHED':
                        game.finished = True
                    
                game.save()
                
                # Update linked pool matches
                if game.finished and hasattr(game, 'pool_matches'):
                    for pool_match in game.pool_matches.all():
                        pool_match.update_from_game()
                
            return True
        else:
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return False
    
    def update_standings(self):
        """Update standings table using the API"""
        url = f"{self.base_url}/competitions/{self.championship.external_api_id}/standings"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Assume first table (usually the main league table)
            if data.get('standings') and len(data['standings']) > 0:
                table = data['standings'][0]['table']
                
                for position_data in table:
                    try:
                        team = Team.objects.get(
                            external_api_id=str(position_data['team']['id']),
                            championship=self.championship
                        )
                        
                        standing, _ = Standing.objects.update_or_create(
                            championship=self.championship,
                            team=team,
                            defaults={
                                'position': position_data['position'],
                                'played': position_data['playedGames'],
                                'won': position_data['won'],
                                'drawn': position_data['draw'],
                                'lost': position_data['lost'],
                                'goals_for': position_data['goalsFor'],
                                'goals_against': position_data['goalsAgainst'],
                                'points': position_data['points'],
                            }
                        )
                    except Team.DoesNotExist:
                        logger.warning(f"Team with ID {position_data['team']['id']} not found")
                
            return True
        else:
            logger.error(f"API Standings Error: {response.status_code} - {response.text}")
            return False
    
    def _map_status(self, api_status):
        """Map API status to our model"""
        status_map = {
            'SCHEDULED': 'scheduled',
            'LIVE': 'live',
            'IN_PLAY': 'live',
            'PAUSED': 'live',
            'FINISHED': 'finished',
            'POSTPONED': 'postponed',
            'SUSPENDED': 'postponed',
            'CANCELED': 'canceled',
        }
        return status_map.get(api_status, 'scheduled')

# Factory for API service selection
def get_api_service(championship):
    """Return the appropriate API service for the championship"""
    service_map = {
        'football-data': FootballDataApiService,
        # Implement other API adapters as needed
    }
    
    service_class = service_map.get(championship.api_provider)
    if not service_class:
        return None
        
    return service_class(championship)