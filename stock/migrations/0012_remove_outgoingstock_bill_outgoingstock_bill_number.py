# Generated by Django 5.0.6 on 2024-06-24 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_outgoingstock_outgoing_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outgoingstock',
            name='bill',
        ),
        migrations.AddField(
            model_name='outgoingstock',
            name='bill_number',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
