# Generated by Django 5.1 on 2024-08-23 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0109_permission_update_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='delete_unit',
            field=models.BooleanField(default=False),
        ),
    ]
