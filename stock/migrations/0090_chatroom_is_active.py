# Generated by Django 5.1 on 2024-08-14 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0089_chatroom_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]