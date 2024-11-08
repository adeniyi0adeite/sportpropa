# Generated by Django 5.0.4 on 2024-10-18 10:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_management', '0009_remove_match_man_of_the_match_and_more'),
        ('user_management', '0003_post_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.userprofile')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_comments', to='match_management.match')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_replies', to='match_management.matchcomment')),
            ],
            options={
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='MatchLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_likes', to='match_management.matchcomment')),
                ('match', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='match_likes', to='match_management.match')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.userprofile')),
            ],
        ),
    ]
