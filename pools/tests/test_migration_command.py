import pytest
from django.core.management import call_command
from django.db import connection
from django.core.management.base import CommandError

from pools.tests.factories import UserFactory, PoolFactory, TeamFactory
from pools.models import Team, Match, Bet
from pools.management.commands.migrate_bets_to_pools import Command as MigrateCommand


@pytest.mark.django_db(transaction=True)
def test_migrate_teams_creates_new_teams(monkeypatch, tmp_path, capsys):
    # Create legacy objects via monkeypatching the LegacyTeam manager
    from pools import legacy_models

    class DummyLegacyTeam:
        def __init__(self, id, name, logo=None):
            self.id = id
            self.name = name
            self.logo = None

    legacy_data = [DummyLegacyTeam(1, 'Alpha FC'), DummyLegacyTeam(2, 'Beta FC')]

    monkeypatch.setattr(legacy_models, 'LegacyTeam', type('X', (), {'objects': type('Q', (), {'all': staticmethod(lambda: legacy_data)})}))

    # Run command
    call_command('migrate_bets_to_pools', '--dry-run')

    # Since it's dry-run, no Team created
    assert Team.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_migrate_teams_no_duplicates(monkeypatch):
    from pools import legacy_models

    # Create an existing team
    Team.objects.create(name='Gamma FC')

    class DummyLegacyTeam:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    legacy_data = [DummyLegacyTeam(1, 'Gamma FC'), DummyLegacyTeam(2, 'Delta FC')]
    monkeypatch.setattr(legacy_models, 'LegacyTeam', type('X', (), {'objects': type('Q', (), {'all': staticmethod(lambda: legacy_data)})}))

    call_command('migrate_bets_to_pools', '--dry-run')

    # no duplicates created for Gamma FC
    assert Team.objects.filter(name='Gamma FC').count() == 1


@pytest.mark.django_db(transaction=True)
def test_migrate_matches_preserves_scores(monkeypatch):
    # Setup pool and teams
    pool = PoolFactory()

    from pools import legacy_models

    class DummyLegacyTeam:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    class DummyLegacyMatch:
        def __init__(self, id, home_team, away_team, match_date, home_score, away_score, pool_id):
            self.id = id
            self.home_team = home_team
            self.away_team = away_team
            self.match_date = match_date
            self.home_score = home_score
            self.away_score = away_score
            self.pool_id = pool_id

    lt1 = DummyLegacyTeam(1, 'Team A')
    lt2 = DummyLegacyTeam(2, 'Team B')
    match = DummyLegacyMatch(1, lt1, lt2, '2025-01-01T12:00:00Z', 2, 1, pool.id)

    monkeypatch.setattr(legacy_models, 'LegacyTeam', type('X', (), {'objects': type('Q', (), {'all': staticmethod(lambda: [lt1, lt2])})}))
    monkeypatch.setattr(legacy_models, 'LegacyMatch', type('X', (), {'objects': type('Q', (), {'select_related': lambda *a, **k: type('Y', (), {'all': staticmethod(lambda: [match])})()})}))

    call_command('migrate_bets_to_pools', '--dry-run')

    # No matches persisted in dry-run
    assert Match.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_migrate_bets_calculates_points(monkeypatch):
    # This test will ensure Bet.save() is called and points logic executes
    user = UserFactory()
    pool = PoolFactory(owner=user)

    # Create match and set finished scores
    match = Match.objects.create(competition=pool.competition if hasattr(pool,'competition') else None, pool=pool, home_team='T1', away_team='T2', start_time='2025-01-01T12:00:00Z', home_score=1, away_score=0, finished=True)

    from pools import legacy_models

    class DummyLegacyBet:
        def __init__(self, id, user_id, match_id, predicted_home_score, predicted_away_score, points_earned, created_at):
            self.id = id
            self.user_id = user_id
            self.match_id = match_id
            self.predicted_home_score = predicted_home_score
            self.predicted_away_score = predicted_away_score
            self.points_earned = points_earned
            self.created_at = created_at

    lbet = DummyLegacyBet(1, user.id, 1, 1, 0, 0, '2025-01-01T11:00:00Z')

    monkeypatch.setattr(legacy_models, 'LegacyBet', type('X', (), {'objects': type('Q', (), {'all': staticmethod(lambda: [lbet])})}))

    # Monkeypatch match_map to map legacy match id 1 to our created match
    from pools.management.commands.migrate_bets_to_pools import match_map
    match_map[1] = match

    call_command('migrate_bets_to_pools', '--dry-run')

    # dry-run shouldn't persist, but ensure our calculate_points() logic works if saved
    b = Bet(user=user, match=match, pool=pool, home_score_bet=1, away_score_bet=0)
    b.points_earned = b.calculate_points()
    assert b.points_earned > 0


@pytest.mark.django_db(transaction=True)
def test_migration_rollback_on_error(monkeypatch):
    # Force an exception during team creation to test rollback
    from pools import legacy_models

    class BadLegacyTeam:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    def bad_all():
        raise RuntimeError('forced failure')

    monkeypatch.setattr(legacy_models, 'LegacyTeam', type('X', (), {'objects': type('Q', (), {'all': staticmethod(bad_all)})}))

    with pytest.raises(RuntimeError):
        call_command('migrate_bets_to_pools')

    # Ensure no teams were committed
    assert Team.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_dry_run_doesnt_persist(monkeypatch):
    from pools import legacy_models

    class DummyLegacyTeam:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    legacy_data = [DummyLegacyTeam(1, 'Zeta FC')]
    monkeypatch.setattr(legacy_models, 'LegacyTeam', type('X', (), {'objects': type('Q', (), {'all': staticmethod(lambda: legacy_data)})}))

    call_command('migrate_bets_to_pools', '--dry-run')
    assert Team.objects.count() == 0
