# Generated by Django 5.0.4 on 2024-09-06 15:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('competition_management', '0021_vote'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwardCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('best_player', 'Best Player'), ('top_scorer', 'Top Scorer'), ('best_goalkeeper', 'Best Goalkeeper'), ('best_team', 'Best Team')], max_length=50)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competition_management.competition')),
                ('nominees', models.ManyToManyField(blank=True, to='competition_management.player')),
                ('teams', models.ManyToManyField(blank=True, to='competition_management.team')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('category', models.CharField(choices=[('best_player', 'Best Player'), ('top_scorer', 'Top Scorer'), ('best_goalkeeper', 'Best Goalkeeper'), ('best_team', 'Best Team')], max_length=50)),
                ('num_of_votes', models.PositiveIntegerField(default=1)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_status', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competition_management.competition')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_votes', to='competition_management.player')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_votes', to='competition_management.team')),
            ],
        ),
    ]