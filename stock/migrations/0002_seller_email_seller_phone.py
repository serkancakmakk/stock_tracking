# Generated by Django 5.1 on 2024-09-19 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='seller',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]