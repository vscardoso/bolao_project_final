from django.contrib import admin
from .models import Sport, Competition, Pool, Match, Bet, Participation

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

admin.site.register(Sport)
admin.site.register(Competition)
admin.site.register(Pool, PoolAdmin)
admin.site.register(Match)
admin.site.register(Bet)
admin.site.register(Participation)
