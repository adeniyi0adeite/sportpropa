# Generated by Django 5.0.4 on 2024-09-06 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_vote_transaction_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='confirmation_token',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
