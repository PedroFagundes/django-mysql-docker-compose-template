# Generated by Django 3.1.4 on 2021-04-29 14:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import workspace.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workspace', '0003_auto_20210416_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffInvitation',
            fields=[
                ('code', models.CharField(default=workspace.utils.generate_random_code, max_length=32, primary_key=True, serialize=False, unique=True, verbose_name='code')),
                ('email', models.EmailField(max_length=256, verbose_name='email')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='workspace.workspace', verbose_name='workspace')),
            ],
            options={
                'verbose_name': 'Staff Invitation',
                'verbose_name_plural': 'Staff Invitations',
                'db_table': 'staff_invitation',
            },
        ),
    ]
