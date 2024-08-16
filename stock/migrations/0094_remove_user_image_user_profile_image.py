# Generated by Django 5.1 on 2024-08-14 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0093_rename_chat_room_message_room_message_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image',
        ),
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
    ]
