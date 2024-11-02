# Generated by Django 5.0.4 on 2024-10-08 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0011_awardcategory_hide_vote_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='awardcategory',
            name='category',
            field=models.CharField(choices=[('most_valuable_player', 'MOST VALUABLE PLAYER'), ('man_of_the_match', 'Man of the Match'), ('best_player', 'Best Player'), ('top_scorer', 'Top Scorer'), ('best_goalkeeper', 'Best Goalkeeper'), ('best_team', 'Best Team'), ('best_coach', 'Best Coach')], max_length=50),
        ),
    ]
