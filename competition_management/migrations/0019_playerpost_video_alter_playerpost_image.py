# Generated by Django 5.0.4 on 2024-07-27 12:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0018_delete_cupknockout'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerpost',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='player_videos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov'])]),
        ),
        migrations.AlterField(
            model_name='playerpost',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='player_images/'),
        ),
    ]
