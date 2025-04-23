from django.contrib import admin
from .models import Sport, Competition, Pool, Match, Bet, Participation, Campeonato, Time, Partida

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

@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'temporada', 'esporte', 'inicio', 'fim')
    search_fields = ('nome', 'temporada')
    list_filter = ('esporte',)

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'campeonato')
    search_fields = ('nome', 'sigla')
    list_filter = ('campeonato',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'campeonato', 'rodada', 'data_hora', 'encerrada')
    list_filter = ('campeonato', 'rodada', 'encerrada')
    search_fields = ('time_casa__nome', 'time_visitante__nome')
    date_hierarchy = 'data_hora'

admin.site.register(Sport)
admin.site.register(Competition)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Match)
admin.site.register(Bet)
admin.site.register(Participation)
