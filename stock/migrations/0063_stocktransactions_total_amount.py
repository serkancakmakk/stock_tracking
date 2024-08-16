# Generated by Django 5.0.6 on 2024-07-29 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0062_outgoingbill_outgoing_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktransactions',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
