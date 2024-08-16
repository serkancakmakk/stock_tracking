# Generated by Django 5.0.6 on 2024-08-08 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0074_alter_user_options_alter_user_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='company_code',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255),
        ),
    ]
