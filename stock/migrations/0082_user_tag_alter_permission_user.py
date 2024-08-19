# Generated by Django 5.0.6 on 2024-08-12 08:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0081_permission_add_parameter'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tag',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to=settings.AUTH_USER_MODEL),
        ),
    ]