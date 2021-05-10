# Generated by Django 3.1.4 on 2021-04-16 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_user_verified_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=64, verbose_name='country'),
        ),
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(blank=True, max_length=50, verbose_name='timezone'),
        ),
        migrations.AddField(
            model_name='user',
            name='zip_code',
            field=models.CharField(blank=True, max_length=64, verbose_name='zip code'),
        ),
    ]
