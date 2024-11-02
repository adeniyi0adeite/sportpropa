# Generated by Django 5.0.4 on 2024-09-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_management', '0006_goal_is_penalty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='match_type',
            field=models.CharField(blank=True, choices=[('Round of 16', 'Round of 16'), ('Quarter Final', 'Quarter final'), ('Semi Final', 'Semi final'), ('Third Place', 'Third Place'), ('Final', 'Final')], max_length=20, null=True),
        ),
    ]