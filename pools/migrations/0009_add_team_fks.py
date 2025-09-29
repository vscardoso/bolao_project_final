from django.db import migrations, models
import django.db.models.deletion


def forwards_populate_team_fks(apps, schema_editor):
    """
    Data migration that populates the temporary FK fields home_team_fk and
    away_team_fk on Match by looking up Teams by name. If a Team with the
    given name does not exist, it will be created.

    We use apps.get_model to obtain historical models that match the state at
    migration time.
    """
    Team = apps.get_model('pools', 'Team')
    Match = apps.get_model('pools', 'Match')

    created_teams = 0
    for match in Match.objects.all():
        # home_team and away_team are CharFields containing team names
        home_name = getattr(match, 'home_team', None)
        away_name = getattr(match, 'away_team', None)

        if home_name:
            team, created = Team.objects.get_or_create(name=home_name)
            if created:
                created_teams += 1
            match.home_team_fk_id = team.pk

        if away_name:
            team, created = Team.objects.get_or_create(name=away_name)
            if created:
                created_teams += 1
            match.away_team_fk_id = team.pk

        match.save()

    # optional: write to stdout via schema_editor.connection if needed
    # but migrations should not print extensively; created_teams can be used by ops


def backwards_unpopulate_team_fks(apps, schema_editor):
    """
    Reverse operation for forwards_populate_team_fks: clear the FK fields.
    """
    Match = apps.get_model('pools', 'Match')
    for match in Match.objects.all():
        match.home_team_fk = None
        match.away_team_fk = None
        match.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pools', '0008_standardize_english_names'),
    ]

    operations = [
        # Step 1: add temporary FK fields to Match to allow relational mapping
        migrations.AddField(
            model_name='match',
            name='home_team_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='home_matches', to='pools.team'),
        ),
        migrations.AddField(
            model_name='match',
            name='away_team_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='away_matches', to='pools.team'),
        ),

        # Step 2: data migration populating the FK fields from existing CharFields
        migrations.RunPython(forwards_populate_team_fks, backwards_unpopulate_team_fks),
    ]
