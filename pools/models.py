from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string

class Sport(models.Model):
    """Modelo para categorias de esportes"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, help_text="Classe de ícone FontAwesome", default="fa-futbol")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Esporte'
        verbose_name_plural = 'Esportes'

class Competition(models.Model):
    """Modelo para competições esportivas"""
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='competitions')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='competitions/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date', 'name']
        verbose_name = 'Competição'
        verbose_name_plural = 'Competições'

class Campeonato(models.Model):
    nome = models.CharField(max_length=100)
    temporada = models.CharField(max_length=10)
    esporte = models.ForeignKey(Sport, on_delete=models.CASCADE)
    inicio = models.DateField()
    fim = models.DateField()
    logo = models.ImageField(upload_to='campeonatos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.nome} {self.temporada}"
    
    class Meta:
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"

class Time(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=3)
    escudo = models.ImageField(upload_to='times/', blank=True, null=True)
    campeonato = models.ForeignKey(Campeonato, related_name='times', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Time"
        verbose_name_plural = "Times"

class Partida(models.Model):
    campeonato = models.ForeignKey(Campeonato, related_name='partidas', on_delete=models.CASCADE)
    rodada = models.IntegerField()
    time_casa = models.ForeignKey(Time, related_name='partidas_casa', on_delete=models.CASCADE)
    time_visitante = models.ForeignKey(Time, related_name='partidas_visitante', on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    gols_casa = models.IntegerField(null=True, blank=True)
    gols_visitante = models.IntegerField(null=True, blank=True)
    encerrada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.time_casa} x {self.time_visitante} - Rodada {self.rodada}"
    
    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

class Pool(models.Model):
    """Modelo principal para bolões"""
    STATUS_CHOICES = (
        ('open', 'Aberto'),
        ('locked', 'Fechado'),
        ('finished', 'Encerrado'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Público'),
        ('private', 'Privado'),
    )
    
    # Campos básicos
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=150)
    description = models.TextField(blank=True)
    
    # Relações
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pools')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Participation',
        related_name='joined_pools'
    )
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='pools')
    campeonato = models.ForeignKey(Campeonato, on_delete=models.SET_NULL, null=True, blank=True, related_name='boloes')
    
    # Configurações do bolão
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    max_participants = models.PositiveIntegerField(default=0, help_text="0 para ilimitado")
    importar_jogos_automaticamente = models.BooleanField(default=False)
    
    # Configurações de pontuação personalizadas
    pontos_acerto_exato = models.IntegerField(default=10)  # Placar exato
    pontos_acerto_vencedor_e_diferenca = models.IntegerField(default=5)  # Vencedor e diferença de gols
    pontos_acerto_vencedor = models.IntegerField(default=3)  # Apenas vencedor
    pontos_erro = models.IntegerField(default=0)  # Errou tudo
    
    # Datas importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    betting_deadline = models.DateTimeField(help_text="Data limite para apostas", null=True, blank=True)
    
    # Chave para convites
    invitation_key = models.UUIDField(default=uuid.uuid4, editable=False)
    
    def save(self, *args, **kwargs):
        # Certifique-se de que o slug é gerado a partir do nome
        if not self.slug:
            self.slug = slugify(self.name)
            # Certifica que o slug é único
            orig_slug = self.slug
            counter = 1
            while Pool.objects.filter(slug=self.slug).exists():
                self.slug = f"{orig_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('pools:detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.name
    
    def is_open_for_betting(self):
        from django.utils import timezone
        return self.status == 'open' and (self.betting_deadline is None or self.betting_deadline > timezone.now())
    
    def get_total_pot(self):
        return self.entry_fee * self.participants.count()
    
    def can_join(self, user):
        """Verifica se um usuário pode participar deste bolão"""
        # Se o usuário já é o dono ou participante, não pode entrar novamente
        if user == self.owner or Participation.objects.filter(pool=self, user=user).exists():
            return False
        
        # Se o status não é 'open', não pode entrar
        if self.status != 'open':
            return False
        
        # Se tem limite de participantes e já atingiu, não pode entrar
        if self.max_participants > 0 and self.participants.count() >= self.max_participants:
            return False
        
        # Se é privado, verificar se tem convite (implementação futura)
        if self.visibility == 'private':
            # Aqui você pode verificar se o usuário tem um convite
            # Por enquanto, vamos permitir entrar em bolões privados
            pass
        
        return True
    
    def get_participant_count(self):
        """Retorna o número de participantes do bolão"""
        return self.participants.count()
    
    def importar_jogos_do_campeonato(self):
        if not self.campeonato:
            return False
            
        # Importar jogos do campeonato selecionado
        partidas = Partida.objects.filter(campeonato=self.campeonato)
        count = 0
        
        for partida in partidas:
            jogo, created = Match.objects.get_or_create(
                pool=self,
                round=partida.rodada,
                defaults={
                    'home_team': partida.time_casa.nome,
                    'away_team': partida.time_visitante.nome,
                    'start_time': partida.data_hora,
                    'partida_relacionada': partida
                }
            )
            if created:
                count += 1
                
        return count
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bolão'
        verbose_name_plural = 'Bolões'
        
class Participation(models.Model):
    """Modelo para relação entre usuários e bolões"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('failed', 'Falhou'),
        ('completed', 'Concluído'),  # Adicionado para corresponder ao código
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, blank=True)
    
    class Meta:
        unique_together = ('user', 'pool')
        verbose_name = 'Participação'
        verbose_name_plural = 'Participações'
        
    def __str__(self):
        return f"{self.user.username} em {self.pool.name}"

class Match(models.Model):
    """Modelo para partidas da competição"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    partida_relacionada = models.ForeignKey(
        Partida, on_delete=models.SET_NULL, null=True, blank=True, related_name='jogos_bolao'
    )
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
    
    def atualizar_resultado_automatico(self):
        if self.partida_relacionada and self.partida_relacionada.encerrada:
            self.home_score = self.partida_relacionada.gols_casa
            self.away_score = self.partida_relacionada.gols_visitante
            self.result = self.calcular_resultado()
            self.save()
            
            # Atualizar pontuações das apostas relacionadas
            self.atualizar_pontuacoes_apostas()
    
    def atualizar_pontuacoes_apostas(self):
        pool = self.pool
        apostas = self.bets.all()
        
        for aposta in apostas:
            # Resultado real
            home_real = self.home_score
            away_real = self.away_score
            
            # Aposta do usuário
            home_aposta = aposta.home_bet
            away_aposta = aposta.away_bet
            
            # Valor padrão de pontos
            pontos = pool.pontos_erro
            
            # Acertou placar exato
            if home_real == home_aposta and away_real == away_aposta:
                pontos = pool.pontos_acerto_exato
            
            # Acertou vencedor e diferença de gols
            elif (home_real - away_real) == (home_aposta - away_aposta):
                pontos = pool.pontos_acerto_vencedor_e_diferenca
            
            # Acertou apenas o vencedor ou empate
            elif (home_real > away_real and home_aposta > away_aposta) or \
                 (home_real < away_real and home_aposta < away_aposta) or \
                 (home_real == away_real and home_aposta == away_aposta):
                pontos = pool.pontos_acerto_vencedor
            
            # Atualizar pontuação da aposta
            aposta.points = pontos
            aposta.save()
    
    class Meta:
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
        ordering = ['start_time']

class Bet(models.Model):
    """Modelo para apostas dos usuários"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    home_score_bet = models.PositiveSmallIntegerField()
    away_score_bet = models.PositiveSmallIntegerField()
    points_earned = models.IntegerField(default=0)  # Pontos ganhos pela aposta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'match', 'pool']
        verbose_name = 'Aposta'
        verbose_name_plural = 'Apostas'
    
    def __str__(self):
        return f"{self.user.username}: {self.match.home_team} {self.home_score_bet} x {self.away_score_bet} {self.match.away_team}"
    
    def calculate_points(self):
        """
        Calcula os pontos ganhos com base no resultado real e na aposta.
        Regras:
        - 10 pontos para resultado exato
        - 5 pontos para vencedor correto e diferença de gols (exceto empates com placares diferentes)
        - 3 pontos para vencedor correto ou empate
        - 0 pontos para erro
        """
        if not self.match.finished or self.match.home_score is None or self.match.away_score is None:
            return 0
            
        # Acertou placar exato
        if self.home_score_bet == self.match.home_score and self.away_score_bet == self.match.away_score:
            return 10
            
        # Acertou o vencedor e a diferença de gols
        real_diff = self.match.home_score - self.match.away_score
        bet_diff = self.home_score_bet - self.away_score_bet
        
        # Para empates, vamos usar uma regra especial
        if self.match.home_score == self.match.away_score and self.home_score_bet == self.away_score_bet:
            # Se ambos são empates mas com placares diferentes, é 3 pontos
            if self.match.home_score != self.home_score_bet:
                return 3
                
        # Para outros casos com mesma diferença
        if (real_diff == bet_diff) and (
            (self.match.home_score > self.match.away_score and self.home_score_bet > self.away_score_bet) or
            (self.match.home_score < self.match.away_score and self.home_score_bet < self.away_score_bet)
        ):
            return 5
            
        # Acertou o vencedor ou empate
        real_result = 0 if self.match.home_score == self.match.away_score else (1 if self.match.home_score > self.match.away_score else -1)
        bet_result = 0 if self.home_score_bet == self.away_score_bet else (1 if self.home_score_bet > self.away_score_bet else -1)
        
        if real_result == bet_result:
            return 3
            
        return 0
    
    def save(self, *args, **kwargs):
        if self.match.finished:
            self.points_earned = self.calculate_points()
        super().save(*args, **kwargs)
    
    def clean(self):
        super().clean()
        # Verificar primeiro se o atributo match existe e não é None
        if hasattr(self, 'match') and self.match and self.match.start_time <= timezone.now():
            raise ValidationError("Não é possível fazer apostas em partidas que já começaram.")

@receiver(post_save, sender=Match)
def update_bets_points(sender, instance, **kwargs):
    """
    Quando uma partida é atualizada como finalizada, recalcula os pontos
    de todas as apostas associadas e atualiza a pontuação dos participantes.
    """
    if instance.finished:
        # Buscar todas as apostas relacionadas a esta partida
        bets = Bet.objects.filter(match=instance)
        
        # Para cada aposta, recalcular pontos
        for bet in bets:
            old_points = bet.points_earned
            new_points = bet.calculate_points()
            
            # Só atualizar se houver mudança nos pontos
            if old_points != new_points:
                bet.points_earned = new_points
                bet.save(update_fields=['points_earned'])
                
                # Atualizar a pontuação do participante no bolão
                participation = Participation.objects.get(user=bet.user, pool=bet.pool)
                participation.points = Bet.objects.filter(
                    user=bet.user, 
                    pool=bet.pool, 
                    match__finished=True
                ).aggregate(total=models.Sum('points_earned'))['total'] or 0
                participation.save(update_fields=['points'])

class Invitation(models.Model):
    """Modelo para convites de bolões"""
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('declined', 'Recusado'),
    )
    
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='invitations')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient_email = models.EmailField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    code = models.CharField(max_length=50, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Gerar código único para o convite se for novo
        if not self.code:
            self.code = get_random_string(length=20)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Convite de {self.sender.username} para {self.recipient_email} - {self.pool.name}"
    
    class Meta:
        unique_together = ('pool', 'recipient_email')
        verbose_name = 'Convite'
        verbose_name_plural = 'Convites'
