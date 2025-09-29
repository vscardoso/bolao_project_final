from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pools', '0009_add_team_fks'),
    ]

    operations = [
        # Remove the old CharField team name columns
        migrations.RemoveField(
            model_name='match',
            name='home_team',
        ),
        migrations.RemoveField(
            model_name='match',
            name='away_team',
        ),

        # Rename temporary FK fields to final names
        migrations.RenameField(
            model_name='match',
            old_name='home_team_fk',
            new_name='home_team',
        ),
        migrations.RenameField(
            model_name='match',
            old_name='away_team_fk',
            new_name='away_team',
        ),

        # Make the foreign keys non-nullable (required). If your dataset
        # contains matches without teams, this operation will fail; ensure the
        # previous data migration populated all FK fields.
        migrations.AlterField(
            model_name='match',
            name='home_team',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='home_matches', to='pools.team'),
        ),
        migrations.AlterField(
            model_name='match',
            name='away_team',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='away_matches', to='pools.team'),
        ),
    ]
