# Generated by Django 4.1.5 on 2023-01-27 16:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friendship',
            unique_together={('sender', 'receiver')},
        ),
    ]