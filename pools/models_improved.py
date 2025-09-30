# -*- coding: utf-8 -*-
"""
IMPROVED MODELS FOR BETTING SYSTEM
Enhanced database structure with better performance, scalability, and reliability
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
import uuid
import json


class BaseModel(models.Model):
    """Base model with common fields and audit functionality"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_%(class)s_set'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_%(class)s_set'
    )
    
    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Audit log for tracking all changes"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('bet_placed', 'Bet Placed'),
        ('bet_updated', 'Bet Updated'),
        ('match_finished', 'Match Finished'),
        ('points_calculated', 'Points Calculated'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.model_name} at {self.timestamp}"


class Sport(BaseModel):
    """Sports categories (Football, Basketball, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon classes")
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Sport"
        verbose_name_plural = "Sports"


class Competition(BaseModel):
    """Sports competitions/leagues"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='competitions')
    season = models.CharField(max_length=20)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='competitions/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    # API Integration
    api_provider = models.CharField(
        max_length=50, blank=True,
        choices=[
            ('football-data', 'Football-Data.org'),
            ('api-football', 'API-Football'),
            ('sportmonks', 'SportMonks'),
            ('manual', 'Manual Update')
        ]
    )
    external_api_id = models.CharField(max_length=100, blank=True, db_index=True)
    api_endpoint = models.URLField(blank=True)
    auto_update = models.BooleanField(default=False)
    update_frequency_hours = models.PositiveIntegerField(default=24)
    last_api_sync = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.season}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} {self.season}"
    
    class Meta:
        ordering = ['-start_date', 'name']
        unique_together = ['name', 'season']
        indexes = [
            models.Index(fields=['sport', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]


class Team(BaseModel):
    """Teams participating in competitions"""
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20, blank=True)
    code = models.CharField(max_length=5, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='teams/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#000000")
    secondary_color = models.CharField(max_length=7, default="#FFFFFF")
    
    # Competition relationship
    competitions = models.ManyToManyField(Competition, related_name='teams')
    
    # API Integration
    external_api_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Statistics
    total_matches = models.PositiveIntegerField(default=0)
    total_wins = models.PositiveIntegerField(default=0)
    total_draws = models.PositiveIntegerField(default=0)
    total_losses = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['competitions']),
        ]


class Match(BaseModel):
    """Unified match model - single source of truth"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    RESULT_CHOICES = [
        ('1', 'Home Win'),
        ('X', 'Draw'),
        ('2', 'Away Win'),
    ]
    
    # Basic match info
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='matches')
    round_number = models.PositiveIntegerField(default=1)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    
    # Schedule
    scheduled_datetime = models.DateTimeField(db_index=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    
    # Scores
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    home_score_ht = models.PositiveIntegerField(null=True, blank=True)  # Half-time
    away_score_ht = models.PositiveIntegerField(null=True, blank=True)  # Half-time
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', db_index=True)
    result = models.CharField(max_length=1, choices=RESULT_CHOICES, null=True, blank=True, db_index=True)
    
    # API Integration
    external_api_id = models.CharField(max_length=100, blank=True, db_index=True)
    api_last_update = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_bets = models.PositiveIntegerField(default=0)
    
    def clean(self):
        if self.home_team == self.away_team:
            raise ValidationError("Home and away teams cannot be the same")
    
    def calculate_result(self):
        """Calculate match result based on scores"""
        if self.home_score is None or self.away_score is None:
            return None
        
        if self.home_score > self.away_score:
            return '1'
        elif self.home_score < self.away_score:
            return '2'
        else:
            return 'X'
    
    def save(self, *args, **kwargs):
        # Auto-calculate result
        if self.status == 'finished' and self.home_score is not None and self.away_score is not None:
            self.result = self.calculate_result()
        
        super().save(*args, **kwargs)
        
        # Clear related caches
        self.clear_caches()
    
    def clear_caches(self):
        """Clear related caches when match is updated"""
        cache_keys = [
            f'match_{self.id}_stats',
            f'competition_{self.competition.id}_matches',
            f'team_{self.home_team.id}_matches',
            f'team_{self.away_team.id}_matches',
        ]
        cache.delete_many(cache_keys)
    
    def get_bets_count(self):
        """Get number of bets for this match"""
        return self.bets.count()
    
    def is_betting_open(self):
        """Check if betting is still open for this match"""
        return self.status == 'scheduled' and self.scheduled_datetime > timezone.now()
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['scheduled_datetime']
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        indexes = [
            models.Index(fields=['competition', 'status']),
            models.Index(fields=['scheduled_datetime', 'status']),
            models.Index(fields=['home_team', 'away_team']),
            models.Index(fields=['status', 'result']),
        ]


class Pool(BaseModel):
    """Betting pools"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('locked', 'Locked'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('invited_only', 'Invited Only'),
    ]
    
    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Relationships
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pools')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='pools')
    matches = models.ManyToManyField(Match, related_name='pools', blank=True)
    
    # Settings
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_participants = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    visibility = models.CharField(max_length=15, choices=VISIBILITY_CHOICES, default='public')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft', db_index=True)
    
    # Betting rules
    betting_deadline_hours = models.PositiveIntegerField(default=0, help_text="Hours before match start")
    allow_bet_changes = models.BooleanField(default=True)
    
    # Scoring system
    exact_score_points = models.PositiveIntegerField(default=10)
    correct_difference_points = models.PositiveIntegerField(default=5)
    correct_result_points = models.PositiveIntegerField(default=3)
    wrong_prediction_points = models.PositiveIntegerField(default=0)
    
    # Auto-import settings
    auto_import_matches = models.BooleanField(default=False)
    auto_update_results = models.BooleanField(default=True)
    
    # Security
    invitation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Statistics
    total_participants = models.PositiveIntegerField(default=0)
    total_bets = models.PositiveIntegerField(default=0)
    total_prize_pool = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Pool.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('pools:detail', kwargs={'slug': self.slug})
    
    def can_user_join(self, user):
        """Check if user can join this pool"""
        if self.status != 'open':
            return False, "Pool is not open for new participants"
        
        if self.participants.filter(id=user.id).exists():
            return False, "User is already a participant"
        
        if self.max_participants > 0 and self.total_participants >= self.max_participants:
            return False, "Pool is full"
        
        return True, "Can join"
    
    def get_leaderboard(self):
        """Get leaderboard with caching"""
        cache_key = f'pool_{self.id}_leaderboard'
        leaderboard = cache.get(cache_key)
        
        if leaderboard is None:
            from django.db.models import Sum
            leaderboard = self.participations.select_related('user').annotate(
                total_points=Sum('bets__points_earned')
            ).order_by('-total_points', 'user__username')
            
            cache.set(cache_key, list(leaderboard), 300)  # Cache for 5 minutes
        
        return leaderboard
    
    def update_statistics(self):
        """Update pool statistics"""
        self.total_participants = self.participations.count()
        self.total_bets = Bet.objects.filter(pool=self).count()
        self.total_prize_pool = self.entry_fee * self.total_participants
        self.save(update_fields=['total_participants', 'total_bets', 'total_prize_pool'])
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['competition', 'status']),
            models.Index(fields=['visibility', 'status']),
        ]


class Participation(BaseModel):
    """User participation in pools"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='participations')
    
    # Payment
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Statistics
    total_points = models.IntegerField(default=0, db_index=True)
    total_bets = models.PositiveIntegerField(default=0)
    correct_predictions = models.PositiveIntegerField(default=0)
    
    # Ranking
    current_position = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    best_position = models.PositiveIntegerField(null=True, blank=True)
    
    def update_statistics(self):
        """Update participation statistics"""
        from django.db.models import Sum, Count, Q
        
        bets = Bet.objects.filter(user=self.user, pool=self.pool)
        
        self.total_points = bets.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
        self.total_bets = bets.count()
        self.correct_predictions = bets.filter(points_earned__gt=0).count()
        
        self.save(update_fields=['total_points', 'total_bets', 'correct_predictions'])
        
        # Clear pool leaderboard cache
        cache.delete(f'pool_{self.pool.id}_leaderboard')
    
    def __str__(self):
        return f"{self.user.username} in {self.pool.name}"
    
    class Meta:
        unique_together = ['user', 'pool']
        ordering = ['-total_points', 'user__username']
        indexes = [
            models.Index(fields=['pool', 'total_points']),
            models.Index(fields=['user', 'total_points']),
        ]


class Bet(BaseModel):
    """User predictions for matches"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, related_name='bets')
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name='bets')
    
    # Predictions
    home_score_prediction = models.PositiveIntegerField()
    away_score_prediction = models.PositiveIntegerField()
    
    # Results
    points_earned = models.IntegerField(default=0, db_index=True)
    is_correct = models.BooleanField(default=False, db_index=True)
    
    # Metadata
    confidence_level = models.PositiveIntegerField(default=5, help_text="1-10 scale")
    bet_version = models.PositiveIntegerField(default=1)  # For tracking changes
    
    def clean(self):
        # Check if betting is still allowed
        if self.match.scheduled_datetime <= timezone.now():
            raise ValidationError("Cannot bet on matches that have already started")
        
        # Check if user is participant in the pool
        if not Participation.objects.filter(user=self.user, pool=self.pool).exists():
            raise ValidationError("User must be a participant in the pool")
    
    def calculate_points(self):
        """Calculate points based on prediction accuracy"""
        if not self.match.status == 'finished':
            return 0
        
        home_actual = self.match.home_score
        away_actual = self.match.away_score
        home_pred = self.home_score_prediction
        away_pred = self.away_score_prediction
        
        # Exact score
        if home_actual == home_pred and away_actual == away_pred:
            return self.pool.exact_score_points
        
        # Correct goal difference
        if (home_actual - away_actual) == (home_pred - away_pred):
            return self.pool.correct_difference_points
        
        # Correct result (win/draw/loss)
        actual_result = self.match.calculate_result()
        predicted_result = '1' if home_pred > away_pred else ('2' if home_pred < away_pred else 'X')
        
        if actual_result == predicted_result:
            return self.pool.correct_result_points
        
        return self.pool.wrong_prediction_points
    
    def save(self, *args, **kwargs):
        # Calculate points if match is finished
        if self.match.status == 'finished':
            self.points_earned = self.calculate_points()
            self.is_correct = self.points_earned > 0
        
        super().save(*args, **kwargs)
        
        # Update participation statistics
        if hasattr(self, 'participation'):
            self.participation.update_statistics()
    
    def __str__(self):
        return f"{self.user.username}: {self.match} ({self.home_score_prediction}-{self.away_score_prediction})"
    
    class Meta:
        unique_together = ['user', 'match', 'pool']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'pool']),
            models.Index(fields=['match', 'pool']),
            models.Index(fields=['points_earned', 'is_correct']),
        ]


class Notification(BaseModel):
    """User notifications"""
    TYPE_CHOICES = [
        ('pool_invitation', 'Pool Invitation'),
        ('match_starting', 'Match Starting Soon'),
        ('match_result', 'Match Result'),
        ('bet_reminder', 'Betting Reminder'),
        ('ranking_update', 'Ranking Update'),
        ('pool_finished', 'Pool Finished'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Status
    is_read = models.BooleanField(default=False, db_index=True)
    is_sent = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE, null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    
    # Delivery
    send_email = models.BooleanField(default=True)
    send_push = models.BooleanField(default=False)
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['type', 'is_sent']),
            models.Index(fields=['priority', 'created_at']),
        ]


# Signals for automatic actions
@receiver(post_save, sender=Match)
def update_match_bets(sender, instance, **kwargs):
    """Update bet points when match finishes"""
    if instance.status == 'finished' and instance.result:
        bets = Bet.objects.filter(match=instance)
        
        for bet in bets:
            old_points = bet.points_earned
            new_points = bet.calculate_points()
            
            if old_points != new_points:
                bet.points_earned = new_points
                bet.is_correct = new_points > 0
                bet.save(update_fields=['points_earned', 'is_correct'])


@receiver(post_save, sender=Bet)
def update_pool_statistics(sender, instance, created, **kwargs):
    """Update pool statistics when bet is created/updated"""
    if created:
        instance.pool.update_statistics()
        instance.match.total_bets = instance.match.bets.count()
        instance.match.save(update_fields=['total_bets'])


@receiver(post_save, sender=Participation)
def update_pool_participants(sender, instance, created, **kwargs):
    """Update pool participant count"""
    if created:
        instance.pool.update_statistics()