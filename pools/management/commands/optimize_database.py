# -*- coding: utf-8 -*-
"""
DATABASE OPTIMIZATION QUERIES
Performance improvements for the betting system
"""

from django.core.management.base import BaseCommand
from django.db import connection
from pools.models import *
import time


class Command(BaseCommand):
    help = 'Optimize database with indexes and performance improvements'
    
    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Apply optimizations')
        parser.add_argument('--analyze', action='store_true', help='Analyze current performance')
        
    def handle(self, *args, **options):
        if options['analyze']:
            self.analyze_performance()
        
        if options['apply']:
            self.apply_optimizations()
    
    def analyze_performance(self):
        """Analyze current database performance"""
        self.stdout.write("🔍 ANALYZING DATABASE PERFORMANCE")
        
        with connection.cursor() as cursor:
            # Check table sizes
            cursor.execute("""
                SELECT 
                    table_name,
                    table_rows,
                    data_length,
                    index_length,
                    (data_length + index_length) as total_size
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'pools_%'
                ORDER BY total_size DESC
            """)
            
            self.stdout.write("\n📊 TABLE SIZES:")
            for row in cursor.fetchall():
                table, rows, data_size, idx_size, total = row
                self.stdout.write(f"  {table}: {rows} rows, {self.format_bytes(total)}")
            
            # Check slow queries
            cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
            slow_log = cursor.fetchone()
            self.stdout.write(f"\n📈 SLOW QUERY LOG: {slow_log[1] if slow_log else 'Unknown'}")
            
            # Check indexes
            cursor.execute("""
                SELECT 
                    table_name,
                    index_name,
                    column_name,
                    cardinality
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE()
                AND table_name LIKE 'pools_%'
                ORDER BY table_name, index_name
            """)
            
            self.stdout.write("\n📑 CURRENT INDEXES:")
            current_table = None
            for row in cursor.fetchall():
                table, index, column, card = row
                if table != current_table:
                    self.stdout.write(f"\n  {table}:")
                    current_table = table
                self.stdout.write(f"    {index}: {column} (card: {card})")
    
    def apply_optimizations(self):
        """Apply database optimizations"""
        self.stdout.write("🚀 APPLYING DATABASE OPTIMIZATIONS")
        
        optimizations = [
            # Composite indexes for frequent queries
            {
                'name': 'pools_bet_user_pool_match',
                'table': 'pools_bet',
                'sql': 'CREATE INDEX idx_bet_user_pool_match ON pools_bet (user_id, pool_id, match_id)'
            },
            {
                'name': 'pools_match_competition_datetime',
                'table': 'pools_match', 
                'sql': 'CREATE INDEX idx_match_comp_datetime ON pools_match (competition_id, start_time)'
            },
            {
                'name': 'pools_participation_pool_points',
                'table': 'pools_participation',
                'sql': 'CREATE INDEX idx_participation_pool_points ON pools_participation (pool_id, points DESC)'
            },
            {
                'name': 'pools_pool_status_visibility',
                'table': 'pools_pool',
                'sql': 'CREATE INDEX idx_pool_status_vis ON pools_pool (status, visibility)'
            },
            # Optimize for leaderboard queries
            {
                'name': 'pools_bet_pool_points',
                'table': 'pools_bet',
                'sql': 'CREATE INDEX idx_bet_pool_points ON pools_bet (pool_id, points_earned DESC)'
            },
            # Optimize for match queries
            {
                'name': 'pools_match_teams_datetime',
                'table': 'pools_match',
                'sql': 'CREATE INDEX idx_match_teams_datetime ON pools_match (home_team_id, away_team_id, start_time)'
            },
        ]
        
        with connection.cursor() as cursor:
            for opt in optimizations:
                try:
                    # Check if index already exists
                    cursor.execute(f"SHOW INDEX FROM {opt['table']} WHERE Key_name = %s", [opt['name'].split('_')[-1]])
                    if cursor.fetchone():
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  {opt['name']}: Index already exists")
                        )
                        continue
                    
                    start_time = time.time()
                    cursor.execute(opt['sql'])
                    duration = time.time() - start_time
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Created {opt['name']} ({duration:.2f}s)"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  {opt['name']}: {str(e)}"
                        )
                    )
            
            # Analyze tables after index creation
            self.stdout.write("\n🔧 ANALYZING TABLES...")
            tables_to_analyze = [
                'pools_bet', 'pools_match', 'pools_participation', 
                'pools_pool', 'pools_team', 'pools_competition'
            ]
            
            for table in tables_to_analyze:
                try:
                    cursor.execute(f"ANALYZE TABLE {table}")
                    self.stdout.write(f"✅ Analyzed {table}")
                except Exception as e:
                    self.stdout.write(f"⚠️  Error analyzing {table}: {e}")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 DATABASE OPTIMIZATION COMPLETE!"))
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        if bytes_value is None:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} TB"