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
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Classes de ícone Font Awesome", blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Esporte"
        verbose_name_plural = "Esportes"

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

class Championship(models.Model):
    name = models.CharField(max_length=100)
    season = models.CharField(max_length=10)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='championships/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    api_provider = models.CharField(max_length=50, blank=True, 
                             choices=[('football-data', 'Football-Data.org'), 
                                    ('api-football', 'API-Football'),
                                    ('sportmonks', 'SportMonks'),
                                    ('manual', 'Manual Update')])
    external_api_id = models.CharField(max_length=100, blank=True)
    api_endpoint = models.CharField(max_length=255, blank=True)
    auto_update = models.BooleanField(default=False)
    update_frequency = models.IntegerField(default=24, help_text="Update frequency in hours")
    last_update = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.season}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} {self.season}"
    
    class Meta:
        verbose_name = "Championship"
        verbose_name_plural = "Championships"

class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    short_name = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='teams/', blank=True, null=True)
    championship = models.ForeignKey(Championship, related_name='teams', on_delete=models.CASCADE)
    primary_color = models.CharField(max_length=7, default="#000000", help_text="Team's main color (HEX code)")
    external_api_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

class Game(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
        ('canceled', 'Canceled'),
    ]
    
    championship = models.ForeignKey(Championship, related_name='games', on_delete=models.CASCADE)
    round = models.IntegerField()
    home_team = models.ForeignKey(Team, related_name='home_games', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_games', on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    finished = models.BooleanField(default=False)
    external_api_id = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - Round {self.round}"
    
    class Meta:
        verbose_name = "Game" 
        verbose_name_plural = "Games"

class Pool(models.Model):
    """Main model for pools"""
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('locked', 'Locked'),
        ('finished', 'Finished'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )
    
    # Basic fields
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)
    
    # Relationships
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pools')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Participation',
        related_name='joined_pools'
    )
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='pools')
    championship = models.ForeignKey(
        'Championship',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="pools"
    )
    
    # Pool settings
    import_matches_automatically = models.BooleanField(default=False)
    exact_score_points = models.PositiveIntegerField(default=10)
    correct_difference_points = models.PositiveIntegerField(default=5)
    correct_winner_points = models.PositiveIntegerField(default=3)
    wrong_points = models.PositiveIntegerField(default=0)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fee to join the pool")
    max_participants = models.IntegerField(default=0, help_text="0 for unlimited")
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    
    # Important dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    betting_deadline = models.DateTimeField(help_text="Deadline for placing bets", null=True, blank=True)
    
    # Invitation key
    invitation_key = models.UUIDField(default=uuid.uuid4, editable=False)
    
    def save(self, *args, **kwargs):
        # Ensure slug is generated from name
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug is unique
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
        """Check if a user can join this pool"""
        # If the user is already the owner or participant, they cannot join again
        if user == self.owner or Participation.objects.filter(pool=self, user=user).exists():
            return False
        
        # If the status is not 'open', they cannot join
        if self.status != 'open':
            return False
        
        # If there is a limit on participants and it has been reached, they cannot join
        if self.max_participants > 0 and self.participants.count() >= self.max_participants:
            return False
        
        # If it is private, check if there is an invitation (future implementation)
        if self.visibility == 'private':
            # Here you can check if the user has an invitation
            # For now, let's allow joining private pools
            pass
        
        return True
    
    def get_participant_count(self):
        """Returns the number of participants in the pool"""
        return self.participants.count()
    
    def import_championship_games(self):
        """Import games from the championship to the pool"""
        if not self.championship:
            return False
            
        # Import games from the selected championship
        games = Game.objects.filter(championship=self.championship)
        count = 0
        
        for game in games:
            match, created = Match.objects.get_or_create(
                pool=self,
                round=game.round,
                defaults={
                    'home_team': game.home_team.name,
                    'away_team': game.away_team.name,
                    'start_time': game.datetime,
                    'related_game': game
                }
            )
            if created:
                count += 1
                
        return count
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pool'
        verbose_name_plural = 'Pools'
        
class Participation(models.Model):
    """Model for user-pool relationships"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, blank=True)
    
    class Meta:
        unique_together = ('user', 'pool')
        verbose_name = 'Participation'
        verbose_name_plural = 'Participations'
        
    def __str__(self):
        return f"{self.user.username} in {self.pool.name}"

class Match(models.Model):
    """Model for matches in a pool"""
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='matches', null=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches', null=True, blank=True)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches', null=True, blank=True)
    start_time = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    result = models.CharField(max_length=1, null=True, blank=True)  # '1' for home win, '2' for away win, 'X' for draw
    related_game = models.ForeignKey(
        Game, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="pool_matches"
    )
    
    def calculate_result(self):
        """Calculate the match result: '1' for home win, '2' for away win, 'X' for draw"""
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return '1'
        elif self.home_score < self.away_score:
            return '2'
        else:
            return 'X'
    
    def update_result_automatically(self):
        if self.related_game and self.related_game.finished:
            self.home_score = self.related_game.home_score
            self.away_score = self.related_game.away_score
            self.result = self.calculate_result()
            self.save()
            
            # Update scores of related bets
            self.update_bet_scores()
    
    def update_bet_scores(self):
        pool = self.pool
        bets = self.bets.all()
        
        for bet in bets:
            # Resultado real
            home_actual = self.home_score
            away_actual = self.away_score
            
            # Aposta do usuário
            home_bet = bet.home_bet
            away_bet = bet.away_bet
            
            # Default points
            points = pool.wrong_points
            
            # Correct exact score
            if home_actual == home_bet and away_actual == away_bet:
                points = pool.exact_score_points
            
            # Correct winner and goal difference
            elif (home_actual - away_actual) == (home_bet - away_bet):
                points = pool.correct_difference_points
            
            # Only correct winner or draw
            elif (home_actual > away_actual and home_bet > away_bet) or \
                 (home_actual < away_actual and home_bet < away_bet) or \
                 (home_actual == away_actual and home_bet == away_bet):
                points = pool.correct_winner_points
            
            # Update bet points
            bet.points = points
            bet.save()
    
    def update_from_game(self):
        if not self.related_game:
            return False
            
        if self.related_game.status == 'finished':
            self.home_score = self.related_game.home_score
            self.away_score = self.related_game.away_score
            self.result = self.calculate_result()
            self.finished = True
            self.save()
            
            # Update bet scores
            self.update_bet_scores()
            return True
            
        return False
    
    class Meta:
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['start_time']

class Bet(models.Model):
    """Model for user bets"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    home_score_bet = models.PositiveSmallIntegerField()
    away_score_bet = models.PositiveSmallIntegerField()
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'match', 'pool']
        verbose_name = 'Bet'
        verbose_name_plural = 'Bets'
    
    def __str__(self):
        return f"{self.user.username}: {self.match.home_team} {self.home_score_bet} x {self.away_score_bet} {self.match.away_team}"
    
    def calculate_points(self):
        """
        Calculate points earned based on the real result and the bet.
        Rules:
        - 10 points for exact result
        - 5 points for correct winner and goal difference (except draws with different scores)
        - 3 points for correct winner or draw
        - 0 points for error
        """
        if not self.match.finished or self.match.home_score is None or self.match.away_score is None:
            return 0
            
        # Exact score match
        if self.home_score_bet == self.match.home_score and self.away_score_bet == self.match.away_score:
            return 10
            
        # Correct winner and goal difference
        real_diff = self.match.home_score - self.match.away_score
        bet_diff = self.home_score_bet - self.away_score_bet
        
        # Special rule for draws
        if self.match.home_score == self.match.away_score and self.home_score_bet == self.away_score_bet:
            if self.match.home_score != self.home_score_bet:
                return 3
                
        # Other cases with same difference
        if (real_diff == bet_diff) and (
            (self.match.home_score > self.match.away_score and self.home_score_bet > self.away_score_bet) or
            (self.match.home_score < self.match.away_score and self.home_score_bet < self.away_score_bet)
        ):
            return 5
            
        # Correct winner or draw
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
        if hasattr(self, 'match') and self.match and self.match.start_time <= timezone.now():
            raise ValidationError("Cannot place bets on matches that have already started.")

@receiver(post_save, sender=Match)
def update_bets_points(sender, instance, **kwargs):
    """
    When a match is updated as finished, recalculate the points
    of all associated bets and update participant scores.
    """
    if instance.finished:
        bets = Bet.objects.filter(match=instance)
        
        for bet in bets:
            old_points = bet.points_earned
            new_points = bet.calculate_points()
            
            if old_points != new_points:
                bet.points_earned = new_points
                bet.save(update_fields=['points_earned'])
                
                participation = Participation.objects.get(user=bet.user, pool=bet.pool)
                participation.points = Bet.objects.filter(
                    user=bet.user, 
                    pool=bet.pool, 
                    match__finished=True
                ).aggregate(total=models.Sum('points_earned'))['total'] or 0
                participation.save(update_fields=['points'])

class Invitation(models.Model):
    """Model for pool invitations"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
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
        if not self.code:
            self.code = get_random_string(length=20)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Invitation from {self.sender.username} to {self.recipient_email} - {self.pool.name}"
    
    class Meta:
        unique_together = ('pool', 'recipient_email')
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'

class Standing(models.Model):
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name="standings")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="standings")
    position = models.PositiveIntegerField()
    played = models.PositiveIntegerField(default=0)
    won = models.PositiveIntegerField(default=0)
    drawn = models.PositiveIntegerField(default=0)
    lost = models.PositiveIntegerField(default=0)
    goals_for = models.PositiveIntegerField(default=0)
    goals_against = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        verbose_name = "Standing"
        verbose_name_plural = "Standings"
        
    def __str__(self):
        return f"{self.team.name} - {self.championship.name} ({self.position}º)"
