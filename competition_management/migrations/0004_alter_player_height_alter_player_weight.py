# Generated by Django 5.0.4 on 2024-05-21 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0003_alter_player_height_alter_player_nationality_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='height',
            field=models.IntegerField(blank=True, default='N/A', null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='weight',
            field=models.IntegerField(blank=True, default='N/A', null=True),
        ),
    ]
