# Generated by Django 5.0.6 on 2024-08-10 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0079_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='add_bill',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permission',
            name='add_definitions',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permission',
            name='add_inventory',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permission',
            name='add_outgoing',
            field=models.BooleanField(default=False),
        ),
    ]
