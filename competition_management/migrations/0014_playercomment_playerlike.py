# Generated by Django 5.0.4 on 2024-05-30 12:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0013_teamcomment_teamlike'),
        ('user_management', '0002_userprofile_favorite_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.userprofile')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_replies', to='competition_management.playercomment')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_comments', to='competition_management.player')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='PlayerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_likes', to='competition_management.playercomment')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='player_likes', to='competition_management.player')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.userprofile')),
            ],
        ),
    ]
