from django.db import models
from users.models import CustomUser
from pools.models import Pool

class Team(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Match(models.Model):
    home_team = models.ForeignKey(Team, related_name='home_matches', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_matches', on_delete=models.CASCADE)
    match_date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='matches')
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.match} ({self.predicted_home_score}x{self.predicted_away_score})"
