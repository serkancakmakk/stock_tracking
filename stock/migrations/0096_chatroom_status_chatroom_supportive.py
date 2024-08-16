# Generated by Django 5.1 on 2024-08-14 21:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0095_chatroom_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='supportive',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='support_team_user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
