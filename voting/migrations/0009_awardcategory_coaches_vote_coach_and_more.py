# Generated by Django 5.0.4 on 2024-09-14 14:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0024_coach_picture'),
        ('voting', '0008_vote_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardcategory',
            name='coaches',
            field=models.ManyToManyField(blank=True, to='competition_management.coach'),
        ),
        migrations.AddField(
            model_name='vote',
            name='coach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coach_votes', to='competition_management.coach'),
        ),
        migrations.AlterField(
            model_name='awardcategory',
            name='category',
            field=models.CharField(choices=[('most_valuable_player', 'MVP'), ('best_player', 'Best Player'), ('top_scorer', 'Top Scorer'), ('best_goalkeeper', 'Best Goalkeeper'), ('best_team', 'Best Team'), ('best_coach', 'Best Coach')], max_length=50),
        ),
    ]
