# Generated by Django 5.1 on 2024-08-15 22:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0098_user_rating_user_support_given'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
