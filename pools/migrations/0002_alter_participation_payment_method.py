# Generated by Django 5.2 on 2025-04-14 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pools', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participation',
            name='payment_method',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
