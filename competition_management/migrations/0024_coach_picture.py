# Generated by Django 5.0.4 on 2024-09-14 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0023_remove_coach_name_coach_first_name_coach_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coach',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='coach_pictures/'),
        ),
    ]
