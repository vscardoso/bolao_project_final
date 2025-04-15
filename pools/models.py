from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Pool(models.Model):
    """Modelo principal para bolões"""
    STATUS_CHOICES = (
        ('open', 'Aberto para Apostas'),
        ('locked', 'Apostas Encerradas'),
        ('finished', 'Encerrado'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Público'),
        ('private', 'Privado'),
    )
    
    # Campos básicos
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Relações
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pools')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='pools')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Participation',
        related_name='participating_pools'
    )
    
    # Configurações do bolão
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    max_participants = models.PositiveIntegerField(default=0, help_text="0 para ilimitado")
    
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
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
    
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
        return f"Aposta de {self.user.username} em {self.match}"
    
    def calculate_points(self):
        """
        Calcula os pontos ganhos com base no resultado real e na aposta.
        Regras:
        - 3 pontos para resultado exato
        - 1 ponto para vencedor correto ou empate
        - 0 pontos para erro
        """
        if not self.match.finished or self.match.home_score is None or self.match.away_score is None:
            return 0
            
        # Acertou placar exato
        if self.home_score_bet == self.match.home_score and self.away_score_bet == self.match.away_score:
            return 3
            
        # Acertou o vencedor ou empate
        real_result = 0 if self.match.home_score == self.match.away_score else (1 if self.match.home_score > self.match.away_score else -1)
        bet_result = 0 if self.home_score_bet == self.away_score_bet else (1 if self.home_score_bet > self.away_score_bet else -1)
        
        if real_result == bet_result:
            return 1
            
        return 0
    
    def save(self, *args, **kwargs):
        if self.match.finished:
            self.points_earned = self.calculate_points()
        super().save(*args, **kwargs)

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
