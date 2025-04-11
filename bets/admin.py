from django.contrib import admin
from .models import Team, Match, Bet

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'match_date', 'home_score', 'away_score', 'pool')
    list_filter = ('pool', 'match_date')
    search_fields = ('home_team__name', 'away_team__name')

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'predicted_home_score', 'predicted_away_score', 'points_earned', 'created_at')
    list_filter = ('match__pool', 'user')
    search_fields = ('user__username', 'match__home_team__name', 'match__away_team__name')
