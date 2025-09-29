from django.contrib import admin
from django.utils.html import format_html
from .models import Sport, Competition, Pool, Match, Bet, Participation, Championship, Team, Game, Standing

class PoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'competition', 'status', 'visibility']  # Removido 'admin'
    list_filter = ['status', 'visibility', 'competition']
    search_fields = ['name', 'description', 'owner__username']
    prepopulated_fields = {'slug': ('name',)}
    # Removido o 'participants' do filter_horizontal porque usa modelo through
    filter_horizontal = []  
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'competition')

@admin.register(Championship)
class ChampionshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'sport', 'start_date', 'end_date')
    search_fields = ('name', 'season')
    list_filter = ('sport',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'championship', 'display_logo')
    search_fields = ('name', 'code')
    list_filter = ('championship',)
    
    def display_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" height="30" />', obj.logo.url)
        return "-"
    display_logo.short_description = 'Logo'

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'championship', 'round', 'datetime', 'status', 'display_score')
    list_filter = ('championship', 'status', 'round')
    search_fields = ('home_team__name', 'away_team__name')
    date_hierarchy = 'datetime'
    
    def display_score(self, obj):
        if obj.status in ['finished', 'live']:
            return f"{obj.home_score} - {obj.away_score}"
        return "-"
    display_score.short_description = 'Score'

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('position', 'team', 'championship', 'played', 'won', 'drawn', 'lost', 'points')
    list_filter = ('championship',)
    search_fields = ('team__name',)

admin.site.register(Sport)
admin.site.register(Competition)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Match)
admin.site.register(Bet)
admin.site.register(Participation)
