# Generated by Django 5.0.4 on 2024-05-28 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition_management', '0008_alter_competition_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='competition',
            name='start_date',
        ),
        migrations.AddField(
            model_name='competition',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]