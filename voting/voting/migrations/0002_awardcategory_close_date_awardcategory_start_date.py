# Generated by Django 5.0.4 on 2024-09-06 16:44

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardcategory',
            name='close_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='awardcategory',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
