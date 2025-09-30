# -*- coding: utf-8 -*-
"""
REAL-TIME DATABASE MONITORING AND ANALYTICS
Monitor performance, identify bottlenecks, and provide insights
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from pools.models import *
from users.models import CustomUser
from django.db.models import Count, Avg, Sum, Q
import time
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Monitor database performance and provide analytics'
    
    def add_arguments(self, parser):
        parser.add_argument('--monitor', action='store_true', help='Start real-time monitoring')
        parser.add_argument('--analytics', action='store_true', help='Generate analytics report')
        parser.add_argument('--health-check', action='store_true', help='Perform health check')
        parser.add_argument('--interval', type=int, default=30, help='Monitoring interval in seconds')
    
    def handle(self, *args, **options):
        if options['monitor']:
            self.start_monitoring(options['interval'])
        elif options['analytics']:
            self.generate_analytics()
        elif options['health_check']:
            self.health_check()
        else:
            self.full_report()
    
    def start_monitoring(self, interval):
        """Start real-time monitoring"""
        self.stdout.write("🔍 STARTING REAL-TIME DATABASE MONITORING")
        self.stdout.write(f"📊 Monitoring interval: {interval} seconds")
        self.stdout.write("Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                self.monitor_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Monitoring stopped")
    
    def monitor_cycle(self):
        """Single monitoring cycle"""
        timestamp = timezone.now().strftime("%H:%M:%S")
        
        with connection.cursor() as cursor:
            # Check active connections
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            connections = cursor.fetchone()
            
            # Check query performance
            cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
            slow_queries = cursor.fetchone()
            
            # Check table locks
            cursor.execute("SHOW STATUS LIKE 'Table_locks_waited'")
            table_locks = cursor.fetchone()
            
            # Application metrics
            active_pools = Pool.objects.filter(status='open').count()
            recent_bets = Bet.objects.filter(created_at__gte=timezone.now() - timedelta(minutes=5)).count()
            online_users = self.get_online_users_count()
            
            # Memory usage
            cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_data'")
            buffer_pages = cursor.fetchone()
            
            self.stdout.write(
                f"[{timestamp}] "
                f"Conn: {connections[1] if connections else 'N/A'} | "
                f"Slow: {slow_queries[1] if slow_queries else 'N/A'} | "
                f"Locks: {table_locks[1] if table_locks else 'N/A'} | "
                f"Pools: {active_pools} | "
                f"Bets(5m): {recent_bets} | "
                f"Users: {online_users}"
            )
    
    def generate_analytics(self):
        """Generate comprehensive analytics report"""
        self.stdout.write("📈 GENERATING DATABASE ANALYTICS REPORT")
        
        # User engagement analytics
        self.stdout.write("\n👥 USER ENGAGEMENT:")
        total_users = CustomUser.objects.count()
        active_users = Participation.objects.values('user').distinct().count()
        betting_users = Bet.objects.values('user').distinct().count()
        
        self.stdout.write(f"  • Total Users: {total_users}")
        self.stdout.write(f"  • Active Users (in pools): {active_users} ({active_users/total_users*100:.1f}%)")
        self.stdout.write(f"  • Betting Users: {betting_users} ({betting_users/total_users*100:.1f}%)")
        
        # Pool analytics
        self.stdout.write("\n🏆 POOL ANALYTICS:")
        pool_stats = Pool.objects.aggregate(
            total=Count('id'),
            avg_participants=Avg('participation__id'),
            total_prize=Sum('entry_fee')
        )
        
        popular_pools = Pool.objects.annotate(
            participant_count=Count('participation')
        ).order_by('-participant_count')[:5]
        
        self.stdout.write(f"  • Total Pools: {pool_stats['total']}")
        self.stdout.write(f"  • Avg Participants: {pool_stats['avg_participants']:.1f}")
        self.stdout.write(f"  • Total Prize Pool: ${pool_stats['total_prize'] or 0:.2f}")
        
        self.stdout.write("\n  🔥 Most Popular Pools:")
        for pool in popular_pools:
            self.stdout.write(f"    {pool.name}: {pool.participant_count} participants")
        
        # Betting analytics
        self.stdout.write("\n🎯 BETTING ANALYTICS:")
        bet_stats = Bet.objects.aggregate(
            total=Count('id'),
            avg_points=Avg('points_earned'),
            correct_bets=Count('id', filter=Q(points_earned__gt=0))
        )
        
        accuracy = (bet_stats['correct_bets'] / bet_stats['total'] * 100) if bet_stats['total'] > 0 else 0
        
        self.stdout.write(f"  • Total Bets: {bet_stats['total']}")
        self.stdout.write(f"  • Average Points: {bet_stats['avg_points']:.2f}")
        self.stdout.write(f"  • Accuracy Rate: {accuracy:.1f}%")
        
        # Match analytics
        self.stdout.write("\n⚽ MATCH ANALYTICS:")
        match_stats = Match.objects.aggregate(
            total=Count('id'),
            finished=Count('id', filter=Q(finished=True))
        )
        
        # Calculate average bets per match manually
        total_matches = match_stats['total']
        total_bets = Bet.objects.count()
        avg_bets = total_bets / total_matches if total_matches > 0 else 0
        
        self.stdout.write(f"  • Total Matches: {match_stats['total']}")
        self.stdout.write(f"  • Finished Matches: {match_stats['finished']}")
        self.stdout.write(f"  • Avg Bets per Match: {avg_bets:.1f}")
        
        # Performance insights
        self.stdout.write("\n⚡ PERFORMANCE INSIGHTS:")
        with connection.cursor() as cursor:
            # Query performance
            cursor.execute("""
                SELECT 
                    table_name,
                    table_rows,
                    avg_row_length,
                    data_length + index_length as total_size
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'pools_%'
                ORDER BY total_size DESC
                LIMIT 5
            """)
            
            self.stdout.write("  📊 Largest Tables:")
            for row in cursor.fetchall():
                table, rows, avg_length, size = row
                self.stdout.write(f"    {table}: {rows} rows, {self.format_bytes(size)}")
            
            # Index usage
            cursor.execute("""
                SELECT 
                    table_name,
                    COUNT(*) as index_count
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'pools_%'
                GROUP BY table_name
                ORDER BY index_count DESC
            """)
            
            self.stdout.write("\n  📑 Index Usage:")
            for row in cursor.fetchall():
                table, count = row
                self.stdout.write(f"    {table}: {count} indexes")
    
    def health_check(self):
        """Perform comprehensive health check"""
        self.stdout.write("🏥 PERFORMING DATABASE HEALTH CHECK")
        
        issues = []
        warnings = []
        
        # Check data integrity
        self.stdout.write("\n🔍 DATA INTEGRITY CHECK:")
        
        # Orphaned bets
        orphaned_bets = Bet.objects.filter(match__isnull=True).count()
        if orphaned_bets > 0:
            issues.append(f"Found {orphaned_bets} orphaned bets")
        
        # Matches without teams
        matches_no_teams = Match.objects.filter(
            Q(home_team__isnull=True) | Q(away_team__isnull=True)
        ).count()
        if matches_no_teams > 0:
            issues.append(f"Found {matches_no_teams} matches without teams")
        
        # Duplicate participations
        from django.db.models import Count
        duplicate_participations = Participation.objects.values('user', 'pool').annotate(
            count=Count('id')
        ).filter(count__gt=1).count()
        if duplicate_participations > 0:
            issues.append(f"Found {duplicate_participations} duplicate participations")
        
        # Check performance
        self.stdout.write("\n⚡ PERFORMANCE CHECK:")
        
        with connection.cursor() as cursor:
            # Check slow query log
            cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
            slow_log = cursor.fetchone()
            if slow_log and slow_log[1] == 'OFF':
                warnings.append("Slow query log is disabled")
            
            # Check query cache
            cursor.execute("SHOW VARIABLES LIKE 'query_cache_type'")
            query_cache = cursor.fetchone()
            if query_cache and query_cache[1] == 'OFF':
                warnings.append("Query cache is disabled")
            
            # Check buffer pool size
            cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size'")
            buffer_size = cursor.fetchone()
            if buffer_size:
                size_mb = int(buffer_size[1]) / 1024 / 1024
                if size_mb < 128:
                    warnings.append(f"InnoDB buffer pool size is small: {size_mb:.0f}MB")
        
        # Check application metrics
        self.stdout.write("\n📱 APPLICATION CHECK:")
        
        # Low engagement pools
        low_engagement = Pool.objects.annotate(
            participant_count=Count('participation')
        ).filter(participant_count__lt=3, status='open').count()
        
        if low_engagement > 10:
            warnings.append(f"{low_engagement} pools have low engagement (<3 participants)")
        
        # Betting activity
        recent_bets = Bet.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        if recent_bets < 10:
            warnings.append(f"Low betting activity: only {recent_bets} bets in last 7 days")
        
        # Report results
        self.stdout.write("\n📋 HEALTH CHECK RESULTS:")
        
        if not issues and not warnings:
            self.stdout.write(self.style.SUCCESS("✅ System is healthy - no issues found!"))
        else:
            if issues:
                self.stdout.write(self.style.ERROR(f"\n❌ CRITICAL ISSUES ({len(issues)}):"))
                for issue in issues:
                    self.stdout.write(f"  • {issue}")
            
            if warnings:
                self.stdout.write(self.style.WARNING(f"\n⚠️  WARNINGS ({len(warnings)}):"))
                for warning in warnings:
                    self.stdout.write(f"  • {warning}")
        
        # Recommendations
        self.stdout.write("\n💡 RECOMMENDATIONS:")
        if orphaned_bets > 0:
            self.stdout.write("  • Run data cleanup: python manage.py cleanup_orphaned_data")
        if low_engagement > 5:
            self.stdout.write("  • Consider pool promotion campaigns")
        if recent_bets < 50:
            self.stdout.write("  • Implement betting reminder notifications")
        
        self.stdout.write("  • Run optimization: python manage.py optimize_database --apply")
        self.stdout.write("  • Monitor regularly: python manage.py monitor_db --monitor")
    
    def full_report(self):
        """Generate full comprehensive report"""
        self.stdout.write("📊 COMPREHENSIVE DATABASE REPORT")
        self.health_check()
        self.generate_analytics()
        
        # Save report to file
        report_data = {
            'timestamp': timezone.now().isoformat(),
            'health_status': 'healthy',  # Would be determined by health check
            'total_users': CustomUser.objects.count(),
            'total_pools': Pool.objects.count(),
            'total_bets': Bet.objects.count(),
            'total_matches': Match.objects.count(),
        }
        
        filename = f"database_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.stdout.write(f"\n💾 Report saved to: {filename}")
    
    def get_online_users_count(self):
        """Get approximate count of online users based on recent activity"""
        # This is a simplified version - in production you'd track sessions
        recent_activity = timezone.now() - timedelta(minutes=15)
        return Bet.objects.filter(created_at__gte=recent_activity).values('user').distinct().count()
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        if bytes_value is None:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"