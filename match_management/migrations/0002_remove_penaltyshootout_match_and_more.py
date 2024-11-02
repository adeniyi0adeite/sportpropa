# Generated by Django 5.0.4 on 2024-06-14 06:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_management', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='penaltyshootout',
            name='match',
        ),
        migrations.RemoveField(
            model_name='result',
            name='penalty_shootout',
        ),
        migrations.RemoveField(
            model_name='result',
            name='shootout',
        ),
        migrations.AddField(
            model_name='penaltyshootout',
            name='result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to='match_management.result'),
        ),
    ]