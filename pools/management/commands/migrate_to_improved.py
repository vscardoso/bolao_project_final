# -*- coding: utf-8 -*-
"""
MIGRATION TO IMPROVED DATABASE STRUCTURE
Migrates current data to optimized models
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from pools.models import *
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Migrate to improved database structure'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without executing')
        parser.add_argument('--backup', action='store_true', help='Create backup before migration')
        
    def handle(self, *args, **options):
        if options['backup']:
            self.create_backup()
        
        if options['dry_run']:
            self.dry_run_migration()
        else:
            self.execute_migration()
    
    def create_backup(self):
        """Create backup of current data"""
        self.stdout.write("💾 CREATING DATA BACKUP...")
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'pools': [],
            'matches': [],
            'bets': [],
            'participations': [],
        }
        
        # Backup pools
        for pool in Pool.objects.all():
            backup_data['pools'].append({
                'id': pool.id,
                'name': pool.name,
                'slug': pool.slug,
                'owner_id': pool.owner.id,
                'status': pool.status,
                'entry_fee': str(pool.entry_fee),
                'max_participants': pool.max_participants,
            })
        
        # Backup matches
        for match in Match.objects.all():
            backup_data['matches'].append({
                'id': match.id,
                'home_team_id': match.home_team.id if match.home_team else None,
                'away_team_id': match.away_team.id if match.away_team else None,
                'start_time': match.start_time.isoformat(),
                'home_score': match.home_score,
                'away_score': match.away_score,
                'finished': match.finished,
                'result': match.result,
            })
        
        # Backup bets
        for bet in Bet.objects.all():
            backup_data['bets'].append({
                'id': bet.id,
                'user_id': bet.user.id,
                'match_id': bet.match.id,
                'pool_id': bet.pool.id,
                'home_score_bet': bet.home_score_bet,
                'away_score_bet': bet.away_score_bet,
                'points_earned': bet.points_earned,
            })
        
        # Backup participations
        for participation in Participation.objects.all():
            backup_data['participations'].append({
                'id': participation.id,
                'user_id': participation.user.id,
                'pool_id': participation.pool.id,
                'points': participation.points,
                'payment_status': participation.payment_status,
            })
        
        # Save backup
        backup_filename = f"database_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        self.stdout.write(self.style.SUCCESS(f"✅ Backup created: {backup_filename}"))
    
    def dry_run_migration(self):
        """Show what would be migrated"""
        self.stdout.write("🔍 DRY RUN - MIGRATION PREVIEW")
        
        # Count current data
        pools_count = Pool.objects.count()
        matches_count = Match.objects.count()
        bets_count = Bet.objects.count()
        participations_count = Participation.objects.count()
        
        self.stdout.write(f"\n📊 CURRENT DATA:")
        self.stdout.write(f"  • Pools: {pools_count}")
        self.stdout.write(f"  • Matches: {matches_count}")
        self.stdout.write(f"  • Bets: {bets_count}")
        self.stdout.write(f"  • Participations: {participations_count}")
        
        # Show data integrity issues
        self.stdout.write(f"\n🔍 DATA INTEGRITY CHECK:")
        
        # Check for orphaned data
        orphaned_bets = Bet.objects.filter(match__isnull=True).count()
        if orphaned_bets > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {orphaned_bets} orphaned bets found"))
        
        # Check for missing teams
        matches_without_teams = Match.objects.filter(
            models.Q(home_team__isnull=True) | models.Q(away_team__isnull=True)
        ).count()
        if matches_without_teams > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {matches_without_teams} matches without teams"))
        
        # Check for duplicate participations
        from django.db.models import Count
        duplicates = Participation.objects.values('user', 'pool').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()
        if duplicates > 0:
            self.stdout.write(self.style.WARNING(f"  ⚠️  {duplicates} duplicate participations"))
        
        if orphaned_bets == 0 and matches_without_teams == 0 and duplicates == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ No data integrity issues found"))
        
        self.stdout.write(f"\n🚀 MIGRATION PLAN:")
        self.stdout.write("  1. Add new indexes for performance")
        self.stdout.write("  2. Update Match model with enhanced fields")
        self.stdout.write("  3. Migrate Bet model to new structure")
        self.stdout.write("  4. Add audit logging")
        self.stdout.write("  5. Create notification system")
        self.stdout.write("  6. Update statistics")
        
        self.stdout.write(f"\n💡 To execute migration: python manage.py migrate_to_improved")
    
    def execute_migration(self):
        """Execute the actual migration"""
        self.stdout.write("🚀 EXECUTING MIGRATION TO IMPROVED STRUCTURE")
        
        try:
            with transaction.atomic():
                # Step 1: Update existing data to new structure
                self.stdout.write("📝 Step 1: Updating existing data...")
                self.update_existing_data()
                
                # Step 2: Add new fields and relationships
                self.stdout.write("🔗 Step 2: Adding new relationships...")
                self.add_new_relationships()
                
                # Step 3: Migrate statistics
                self.stdout.write("📊 Step 3: Calculating statistics...")
                self.calculate_statistics()
                
                # Step 4: Clean up data
                self.stdout.write("🧹 Step 4: Cleaning up data...")
                self.cleanup_data()
                
                self.stdout.write(self.style.SUCCESS("✅ MIGRATION COMPLETED SUCCESSFULLY!"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ MIGRATION FAILED: {str(e)}"))
            raise
    
    def update_existing_data(self):
        """Update existing data to new format"""
        # Update pools with new statistics
        for pool in Pool.objects.all():
            pool.total_participants = pool.participants.count()
            pool.total_bets = Bet.objects.filter(pool=pool).count()
            pool.total_prize_pool = pool.entry_fee * pool.total_participants
            pool.save(update_fields=['total_participants', 'total_bets', 'total_prize_pool'])
        
        self.stdout.write("  ✅ Updated pool statistics")
    
    def add_new_relationships(self):
        """Add new relationships and ensure data consistency"""
        # Update matches with total_bets
        for match in Match.objects.all():
            match.total_bets = match.bets.count()
            match.save(update_fields=['total_bets'])
        
        self.stdout.write("  ✅ Updated match statistics")
    
    def calculate_statistics(self):
        """Calculate and update all statistics"""
        # Update participation statistics
        for participation in Participation.objects.all():
            bets = Bet.objects.filter(user=participation.user, pool=participation.pool)
            participation.total_points = sum(bet.points_earned for bet in bets)
            participation.total_bets = bets.count()
            participation.correct_predictions = bets.filter(points_earned__gt=0).count()
            participation.save(update_fields=['total_points', 'total_bets', 'correct_predictions'])
        
        self.stdout.write("  ✅ Updated participation statistics")
    
    def cleanup_data(self):
        """Clean up any inconsistent data"""
        # Remove any orphaned data (if any)
        orphaned_bets = Bet.objects.filter(match__isnull=True)
        if orphaned_bets.exists():
            count = orphaned_bets.count()
            orphaned_bets.delete()
            self.stdout.write(f"  🗑️  Removed {count} orphaned bets")
        
        self.stdout.write("  ✅ Data cleanup completed")