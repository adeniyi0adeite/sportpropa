# Generated by Django 5.0.4 on 2024-09-13 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0021_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='is_school_competition',
            field=models.BooleanField(default=False),
        ),
    ]