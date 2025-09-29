import logging
from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from django.utils import timezone

from pools.legacy_models import LegacyTeam, LegacyMatch, LegacyBet
from pools.models import Team, Match, Bet, Pool
from django.contrib.auth import get_user_model
from django.db import connection, ProgrammingError


logger = logging.getLogger(__name__)


def simple_progress(current, total, prefix=''):
    """Print a simple progress indicator."""
    if total == 0:
        return
    pct = int(current / total * 100)
    bar = ('#' * (pct // 2)).ljust(50)
    print(f"{prefix} |{bar}| {pct}% ({current}/{total})", end='\r')


class Command(BaseCommand):
    help = 'Migrate data from legacy bets tables into pools app models'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Simulate migration without writing to DB')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        User = get_user_model()

        logger.info('Starting migration from bets -> pools. dry_run=%s', dry_run)

        # Counters and maps
        stats = defaultdict(int)
        errors = []
        warnings = []

        team_map = {}  # legacy_team_id -> Team instance
        match_map = {}  # legacy_match_id -> Match instance

        # Use atomic transaction; if dry_run, mark for rollback at end
        with transaction.atomic():
            try:
                # Pre-check: ensure legacy tables exist to avoid ProgrammingError
                existing_tables = connection.introspection.table_names()
                missing = []
                for tbl in ('bets_team', 'bets_match', 'bets_bet'):
                    if tbl not in existing_tables:
                        missing.append(tbl)

                if missing:
                    msg = f"Legacy tables not found: {', '.join(missing)}. Nothing to migrate."
                    logger.warning(msg)
                    self.stdout.write(self.style.WARNING(msg))
                    return

                # --------- TEAMS ---------
                try:
                    legacy_teams = list(LegacyTeam.objects.all())
                except ProgrammingError as e:
                    msg = f"Error accessing legacy tables: {e}"
                    logger.error(msg)
                    self.stdout.write(self.style.ERROR(msg))
                    return
                total_teams = len(legacy_teams)
                logger.info('Found %d legacy teams', total_teams)

                for idx, lteam in enumerate(legacy_teams, start=1):
                    simple_progress(idx, total_teams, prefix='Teams')
                    try:
                        # Try to find existing Team by name
                        team = Team.objects.filter(name=lteam.name).first()
                        if team:
                            team_map[lteam.id] = team
                            stats['teams_skipped_existing'] += 1
                            logger.debug('Existing team matched: %s (legacy id=%s)', team.name, lteam.id)
                            continue

                        # Create new Team
                        team = Team(name=lteam.name)
                        # copy logo if present
                        if getattr(lteam, 'logo', None) and getattr(lteam.logo, 'name', None):
                            try:
                                lteam.logo.open('rb')
                                content = lteam.logo.read()
                                filename = lteam.logo.name.split('/')[-1]
                                team.logo.save(filename, ContentFile(content), save=False)
                            except Exception as e:
                                logger.warning('Could not copy logo for legacy team id=%s: %s', lteam.id, e)
                                warnings.append(f'logo copy failed for legacy team {lteam.id}: {e}')

                        team.save()
                        team_map[lteam.id] = team
                        stats['teams_created'] += 1
                        logger.info('Created Team %s (legacy id=%s)', team.name, lteam.id)
                    except Exception as e:
                        logger.exception('Error migrating legacy team id=%s: %s', getattr(lteam, 'id', None), e)
                        errors.append(('team', getattr(lteam, 'id', None), str(e)))

                print()  # newline after progress

                # --------- MATCHES ---------
                legacy_matches = LegacyMatch.objects.select_related('home_team', 'away_team').all()
                total_matches = legacy_matches.count()
                logger.info('Found %d legacy matches', total_matches)

                for idx, lmatch in enumerate(legacy_matches.iterator(), start=1):
                    simple_progress(idx, total_matches, prefix='Matches')
                    try:
                        # Validate pool exists
                        pool = Pool.objects.filter(pk=lmatch.pool_id).first()
                        if not pool:
                            msg = f'Pool id {lmatch.pool_id} not found for legacy match {lmatch.id}'
                            logger.warning(msg)
                            warnings.append(msg)
                            stats['matches_skipped_no_pool'] += 1
                            continue

                        # Determine competition from pool
                        competition = getattr(pool, 'competition', None)
                        if competition is None:
                            msg = f'Pool id {pool.id} has no competition defined; skipping match {lmatch.id}'
                            logger.warning(msg)
                            warnings.append(msg)
                            stats['matches_skipped_no_competition'] += 1
                            continue

                        # Avoid duplicates: consider duplicate if same pool + start_time + teams
                        home_name = lmatch.home_team.name if lmatch.home_team else ''
                        away_name = lmatch.away_team.name if lmatch.away_team else ''
                        start_time = lmatch.match_date

                        exists = Match.objects.filter(
                            pool=pool,
                            start_time=start_time,
                            home_team=home_name,
                            away_team=away_name
                        ).exists()
                        if exists:
                            stats['matches_skipped_duplicate'] += 1
                            logger.debug('Skipping duplicate match %s', lmatch.id)
                            # Map legacy id to existing match for bets mapping
                            existing = Match.objects.filter(
                                pool=pool,
                                start_time=start_time,
                                home_team=home_name,
                                away_team=away_name
                            ).first()
                            match_map[lmatch.id] = existing
                            continue

                        # Create new Match. pools.Match uses CharFields for team names.
                        match = Match(
                            competition=competition,
                            pool=pool,
                            home_team=home_name,
                            away_team=away_name,
                            start_time=start_time,
                            home_score=lmatch.home_score,
                            away_score=lmatch.away_score,
                            finished=bool(lmatch.home_score is not None and lmatch.away_score is not None),
                        )
                        match.result = match.calculate_result() if hasattr(match, 'calculate_result') else None
                        match.save()
                        match_map[lmatch.id] = match
                        stats['matches_created'] += 1
                        logger.info('Created Match %s vs %s (legacy id=%s) in pool %s', home_name, away_name, lmatch.id, pool.id)
                    except Exception as e:
                        logger.exception('Error migrating legacy match id=%s: %s', getattr(lmatch, 'id', None), e)
                        errors.append(('match', getattr(lmatch, 'id', None), str(e)))

                print()  # newline after progress

                # --------- BETS ---------
                legacy_bets = LegacyBet.objects.all()
                total_bets = legacy_bets.count()
                logger.info('Found %d legacy bets', total_bets)

                for idx, lbet in enumerate(legacy_bets.iterator(), start=1):
                    simple_progress(idx, total_bets, prefix='Bets')
                    try:
                        # Validate user
                        user = User.objects.filter(pk=lbet.user_id).first()
                        if not user:
                            msg = f'User id {lbet.user_id} not found for legacy bet {lbet.id}'
                            logger.warning(msg)
                            warnings.append(msg)
                            stats['bets_skipped_no_user'] += 1
                            continue

                        # Validate match mapping
                        new_match = match_map.get(lbet.match_id)
                        if not new_match:
                            msg = f'No migrated match for legacy match id {lbet.match_id} (legacy bet {lbet.id})'
                            logger.warning(msg)
                            warnings.append(msg)
                            stats['bets_skipped_no_match'] += 1
                            continue

                        pool = new_match.pool
                        # Avoid duplicate bets based on unique_together (user, match, pool)
                        exists = Bet.objects.filter(user=user, match=new_match, pool=pool).exists()
                        if exists:
                            stats['bets_skipped_duplicate'] += 1
                            logger.debug('Skipping duplicate bet %s', lbet.id)
                            continue

                        bet = Bet(
                            user=user,
                            match=new_match,
                            pool=pool,
                            home_score_bet=lbet.predicted_home_score,
                            away_score_bet=lbet.predicted_away_score,
                            points_earned=lbet.points_earned or 0,
                            created_at=lbet.created_at,
                        )
                        # Save (Bet.save may compute points if match finished)
                        bet.save()
                        stats['bets_created'] += 1
                        logger.info('Created Bet (legacy id=%s) user=%s match=%s', lbet.id, user.pk, new_match.pk)
                    except Exception as e:
                        logger.exception('Error migrating legacy bet id=%s: %s', getattr(lbet, 'id', None), e)
                        errors.append(('bet', getattr(lbet, 'id', None), str(e)))

                print()  # newline after progress

                # --------- VALIDATION ---------
                # Simple integrity validation: counts
                migrated_teams = stats.get('teams_created', 0) + stats.get('teams_skipped_existing', 0)
                migrated_matches = stats.get('matches_created', 0) + stats.get('matches_skipped_duplicate', 0)
                migrated_bets = stats.get('bets_created', 0) + stats.get('bets_skipped_duplicate', 0)

                logger.info('Migration summary (tentative): teams=%d matches=%d bets=%d', migrated_teams, migrated_matches, migrated_bets)

                # If dry-run, request rollback
                if dry_run:
                    transaction.set_rollback(True)
                    logger.info('Dry-run mode: marking transaction for rollback')

            except Exception as e:
                # Any unexpected exception will rollback due to atomic
                logger.exception('Unexpected error during migration: %s', e)
                raise

        # End outer transaction

        # Final report
        self.stdout.write(self.style.SUCCESS('=== Migration finished ==='))
        self.stdout.write(f"Teams created: {stats.get('teams_created',0)}")
        self.stdout.write(f"Teams skipped existing: {stats.get('teams_skipped_existing',0)}")
        self.stdout.write(f"Matches created: {stats.get('matches_created',0)}")
        self.stdout.write(f"Matches skipped (duplicate): {stats.get('matches_skipped_duplicate',0)}")
        self.stdout.write(f"Matches skipped (no pool): {stats.get('matches_skipped_no_pool',0)}")
        self.stdout.write(f"Bets created: {stats.get('bets_created',0)}")
        self.stdout.write(f"Bets skipped (no user): {stats.get('bets_skipped_no_user',0)}")
        self.stdout.write(f"Bets skipped (no match): {stats.get('bets_skipped_no_match',0)}")
        self.stdout.write(f"Bets skipped (duplicate): {stats.get('bets_skipped_duplicate',0)}")
        self.stdout.write('')

        if warnings:
            self.stdout.write(self.style.WARNING('Warnings:'))
            for w in warnings:
                self.stdout.write(self.style.WARNING(f' - {w}'))

        if errors:
            self.stdout.write(self.style.ERROR('Errors:'))
            for e in errors:
                self.stdout.write(self.style.ERROR(f' - {e}'))

        if dry_run:
            self.stdout.write(self.style.NOTICE('Dry-run mode: no changes were committed.'))
        else:
            self.stdout.write(self.style.SUCCESS('Changes committed to the database.'))
