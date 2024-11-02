# Generated by Django 5.0.4 on 2024-07-27 12:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0019_playerpost_video_alter_playerpost_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerpost',
            name='caption',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='playerpost',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='competition_management.player'),
        ),
    ]
