from django.db import models
from django.conf import settings


"""
Modelos temporários (apenas leitura) mapeando para as tabelas antigas do
app `bets`. Esses modelos têm `managed = False` para que o Django não tente
criar/alterar as tabelas. Use-os exclusivamente em scripts de migração e
management commands que leem os dados legados.
"""


class LegacyTeam(models.Model):
    """Modelo temporário para ler dados da tabela bets_team"""

    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bets_team'
        app_label = 'bets'


class LegacyMatch(models.Model):
    """Modelo temporário para ler dados da tabela bets_match"""

    home_team = models.ForeignKey(
        'LegacyTeam',
        on_delete=models.CASCADE,
        related_name='legacy_home_matches'
    )
    away_team = models.ForeignKey(
        'LegacyTeam',
        on_delete=models.CASCADE,
        related_name='legacy_away_matches'
    )
    match_date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    pool_id = models.IntegerField()  # FK manual para evitar problemas de integridade

    class Meta:
        managed = False
        db_table = 'bets_match'
        app_label = 'bets'


class LegacyBet(models.Model):
    """Modelo temporário para ler dados da tabela bets_bet"""

    user_id = models.IntegerField()
    match_id = models.IntegerField()
    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bets_bet'
        app_label = 'bets'

