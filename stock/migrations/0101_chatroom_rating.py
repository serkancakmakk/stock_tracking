# Generated by Django 5.1 on 2024-08-17 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0100_rename_created_time_chatroom_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='rating',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
